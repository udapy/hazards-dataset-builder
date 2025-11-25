# Makefile for Hazards Dataset Builder

.PHONY: install scrape ingest process export push clean clean-data verify pipeline pipeline-push help

# Default target
all: help

install: ## Install dependencies
	pixi install

scrape: ## Scrape hazards (use LIMIT=N to limit)
	pixi run python main.py --scrape $(if $(LIMIT),--limit $(LIMIT),)

scrape-sample: ## Scrape 5 hazards
	pixi run python main.py --scrape --limit 5

scrape-all: ## Scrape all hazards
	pixi run python main.py --scrape

ingest: ## Ingest universal data
	pixi run python main.py --ingest

process: ## Process PDFs (use LIMIT=N to limit)
	pixi run python main.py --process $(if $(LIMIT),--limit $(LIMIT),)

process-sample: ## Process 5 PDFs
	pixi run python main.py --process --limit 5

process-all: ## Process all PDFs
	pixi run python main.py --process

export: ## Export to HF Dataset (SQLite)
	pixi run python main.py --export

export-lancedb: ## Export to HF Dataset (LanceDB)
	pixi run python main.py --export --use-lancedb --structured

push: ## Push to HF Hub (requires REPO_ID)
	@if [ -z "$(REPO_ID)" ]; then echo "Error: REPO_ID is not set. Usage: make push REPO_ID=username/dataset"; exit 1; fi
	pixi run python main.py --export --use-lancedb --structured --push-to-hub --repo-id $(REPO_ID)

verify: ## Verify data integrity
	pixi run python -m src.verify_data

pipeline: clean-data scrape-all ingest process-all export-lancedb ## Run full pipeline (all data)

pipeline-sample: clean-data scrape-sample ingest process-sample export-lancedb ## Run sample pipeline (5 items)

pipeline-push: pipeline push ## Run full pipeline and push to HF Hub

clean-data: ## Remove only data (keep environment)
	rm -f data/hazards.db
	rm -rf data/lancedb_data
	rm -rf hf_dataset
	rm -rf data/raw/*.pdf
	rm -rf data/universal_downloads

clean: clean-data ## Remove everything including temporary files
	rm -rf .pixi
	rm -rf __pycache__
	rm -rf src/__pycache__

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
