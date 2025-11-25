# Hazards Dataset Builder

A comprehensive toolset for building a hazard dataset for LLM fine-tuning and safety research. This project scrapes hazard information (e.g., from Hazadapt), extracts content from web pages and PDFs, generates embeddings, and exports the data to Hugging Face Dataset format.

## Features

- **Multi-Source Ingestion**: Scrape data from websites (SPA support via Playwright) and process local PDFs.
- **Robust Extraction**: Extract clean text from HTML and PDF documents.
- **Vector Embeddings**: Automatically generate embeddings using `sentence-transformers` (`all-MiniLM-L6-v2`) for semantic search and retrieval.
- **Dual Storage**: Support for both SQLite (simple, local) and LanceDB (vector-native, scalable).
- **Hugging Face Export**: Seamlessly export your dataset to the Hugging Face `datasets` format.
- **Automation**: Makefile included for easy setup, testing, and execution.

## Installation

This project uses `pixi` for dependency management.

```bash
# Install dependencies
make setup
```

## Usage

### 1. Scrape Data

Scrape hazard information from Hazadapt:

```bash
# Scrape all hazards
make scrape

# Scrape a limited number (e.g., for testing)
make scrape ARGS="--limit 5"
```

### 2. Process URLs Manually

You can also process specific URLs:

```bash
# Using LanceDB (Recommended)
pixi run python main.py --urls "https://www.example.com" --use-lancedb

# Using SQLite
pixi run python main.py --urls "https://www.example.com"
```

### 3. Export Dataset

Export the collected data to a Hugging Face Dataset:

```bash
# From LanceDB
make export-lancedb

# From SQLite
make export
```

The dataset will be saved to `hf_dataset_lancedb` (or `hf_dataset`).

## Project Structure

```
hazards-dataset-builder/
├── src/                # Source code
│   ├── process_pdfs.py # PDF processing pipeline
│   ├── store.py        # SQLite storage
│   ├── store_lancedb.py# LanceDB storage
│   └── ...
├── data/               # Data directory
│   ├── raw/            # Raw PDFs
│   ├── hazards.db      # SQLite Database
│   └── lancedb_data/   # LanceDB Dataset
├── scripts/            # Helper scripts
├── tests/              # Tests
├── main.py             # Entry point
└── Makefile            # Command shortcuts
```

## Contributing

1.  Run tests: `make test`
2.  Format code: `pixi run black .` (if installed)

## License

[MIT](LICENSE)
