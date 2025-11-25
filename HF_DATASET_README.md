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

- `source_url` (string): The URL from which the data was scraped.
- `content_type` (string): The type of content (e.g., `text/html+scraped`).
- `extracted_text` (string): The full text content extracted from the hazard page, including sections like Prepare, React, and Recover.
- `embedding` (list of floats): A 384-dimensional vector embedding of the extracted text, generated using `sentence-transformers/all-MiniLM-L6-v2`.
- `metadata` (dict): Additional metadata, including the path to the downloaded PDF version of the hazard guide.

### Example

```json
{
  "source_url": "https://app.hazadapt.com/hazards/active-shooter",
  "content_type": "text/html+scraped",
  "extracted_text": "--- SECTION: Prepare ---\n\n...",
  "embedding": [0.023, -0.12, ...],
  "metadata": {
    "original_url": "https://app.hazadapt.com/hazards/active-shooter",
    "pdf_path": "data/pdfs/active_shooter.pdf"
  }
}
```

## Creation Process

### Data Source

The data is sourced from [Hazadapt](https://app.hazadapt.com/), a safety application providing guides for various hazards.

### Collection Method

Data was collected using a custom Playwright scraper that:

1.  Navigates to each hazard page.
2.  Extracts text from the "Prepare", "React", and "Recover" tabs.
3.  Downloads the associated PDF guide.

### Processing

- **Text Extraction**: Content is extracted from the DOM structure of the web application.
- **Embedding**: Text is embedded using the `all-MiniLM-L6-v2` model to facilitate semantic search and retrieval tasks.

## Intended Use

- **LLM Fine-tuning**: To train models on safety protocols and emergency response.
- **RAG (Retrieval-Augmented Generation)**: As a knowledge base for safety chatbots.
- **Analysis**: For analyzing the structure and content of emergency guides.

## Limitations

- The dataset is a snapshot of the content available at the time of scraping.
- Users should verify critical safety information with official sources.
