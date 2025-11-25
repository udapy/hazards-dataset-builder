---
license: mit
task_categories:
  - text-retrieval
  - text-generation
language:
  - en
tags:
  - safety
  - hazards
  - emergency-preparedness
  - hazadapt
size_categories:
  - n<1K
---

# Hazards Dataset

This dataset contains comprehensive information about various hazards, including preparation, reaction, and recovery steps. It is designed for fine-tuning Large Language Models (LLMs) on safety and emergency response procedures.

## Dataset Structure

The dataset is provided in a format compatible with the Hugging Face `datasets` library.

### Features

- `hazard_type` (string): The high-level category of the hazard (e.g., "Wildfire", "Active Shooter").
- `phase` (string): The phase of emergency management ("Prepare", "React", "Recover").
- `audience` (string): The target audience ("General", "Kids", "Elderly", "Pets", etc.).
- `topic` (string): The specific subject matter of the text chunk (e.g., "Evacuation Routes").
- `content_raw` (string): The exact text content extracted from the source PDF.
- `action_items` (list of strings): A list of actionable steps extracted from the text.
- `sources` (list of dicts): A list of sources/references found in the text, each with a `title` and `url`.
- `source_file` (string): The filename of the source PDF.
- `page_ref` (int): The page number in the source PDF.
- `last_updated` (date): The date the source file was last modified.
- `vector` (list of floats): A 384-dimensional vector embedding of the content.

### Example

```json
{
  "hazard_type": "Avalanche",
  "phase": "Recover",
  "audience": "General",
  "topic": "General Safety",
  "content_raw": "A rapid flow of snow...",
  "action_items": ["Stay calm", "Signal for help"],
  "sources": [{"title": "Avalanche.org", "url": "https://avalanche.org"}],
  "source_file": "avalanche.pdf",
  "page_ref": 1,
  "last_updated": "2025-11-24",
  "vector": [0.023, -0.12, ...]
}
```

## Creation Process

### Data Source

The data is sourced from [Hazadapt](https://app.hazadapt.com/), a safety application providing guides for various hazards.

### Collection Method

Data was collected using a custom pipeline that:

1.  **Scrapes** hazard pages and downloads official PDF guides using Playwright.
2.  **Processes** PDFs using `PyMuPDF4LLM` to extract text and layout information.
3.  **Parses** content into structured fields (Phase, Audience, Topic) using keyword heuristics and layout analysis.
4.  **Embeds** content using `sentence-transformers/all-MiniLM-L6-v2`.

## Intended Use

- **LLM Fine-tuning**: To train models on safety protocols and emergency response.
- **RAG (Retrieval-Augmented Generation)**: As a knowledge base for safety chatbots.
- **Analysis**: For analyzing the structure and content of emergency guides.

## Citation

If you use this dataset in your research or application, please cite it as follows:

```bibtex
@dataset{hazards_dataset_2025,
  author = {Hazards Dataset Builder},
  title = {Hazards Safety Dataset},
  year = {2025},
  publisher = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/your-username/hazards-dataset}},
  note = {Data sourced from Hazadapt}
}
```

## Limitations

- The dataset is a snapshot of the content available at the time of scraping.
- Users should verify critical safety information with official sources.
