import os
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from .store import save_document, init_db
from .embed import generate_embedding

# Ensure DB is initialized
init_db()

BASE_URL = "https://app.hazadapt.com"
HAZARDS_URL = f"{BASE_URL}/hazards"
DATA_DIR = "data/raw"

os.makedirs(DATA_DIR, exist_ok=True)

async def scrape_hazard(page, hazard_url, hazard_name):
    print(f"Scraping {hazard_name} ({hazard_url})...")
    await page.goto(hazard_url)
    await page.wait_for_load_state("networkidle")
    
    # Extract content from tabs
    sections = ["Prepare", "React", "Recover"]
    full_text = ""
    
    for section in sections:
        try:
            # Click the tab
            # Tabs seem to be buttons or links with the section name
            # We use a broad selector to find the text
            await page.get_by_text(section, exact=True).click()
            await page.wait_for_timeout(1000) # Wait for content to render
            
            # Extract text
            # We assume content is in the main container. 
            # A simple strategy is to get all text from the page after clicking the tab, 
            # but that might be noisy. 
            # Let's try to find the specific content container if possible.
            # Based on subagent, content is in p tags.
            content = await page.evaluate("() => document.body.innerText")
            full_text += f"\n\n--- SECTION: {section} ---\n\n{content}"
            
        except Exception as e:
            print(f"Error scraping section {section}: {e}")

    # Handle PDF Download
    pdf_path = None
    try:
        print("Looking for PDF...")
        # Expect a download event
        async with page.expect_download(timeout=5000) as download_info:
            # Click the "View PDF" button. 
            # We use aria-label as identified by subagent
            await page.get_by_label("View PDF button").click()
            
        download = await download_info.value
        # Save to data/pdfs
        safe_name = hazard_name.lower().replace(" ", "_")
        pdf_filename = f"{safe_name}.pdf"
        pdf_path = os.path.join(DATA_DIR, pdf_filename)
        await download.save_as(pdf_path)
        print(f"Downloaded PDF to {pdf_path}")
        
    except Exception as e:
        print(f"Could not download PDF for {hazard_name}: {e}")

    # Save to LanceDB
    # We use the full text as extracted_text
    embedding = generate_embedding(full_text)
    metadata = {
        "original_url": hazard_url,
        "pdf_path": pdf_path if pdf_path else ""
    }
    
    save_document(
        source_url=hazard_url,
        content_type="text/html+scraped",
        extracted_text=full_text,
        embedding=embedding,
        metadata=metadata
    )
    print(f"Saved {hazard_name} to LanceDB.")

import argparse
import asyncio

async def scrape_hazards_async(limit=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Navigating to {HAZARDS_URL}...")
        await page.goto(HAZARDS_URL)
        await page.wait_for_load_state("networkidle")
        
        # Find all hazard links
        links = await page.evaluate('''() => {
            const hazardNameElements = document.querySelectorAll('div > div > div > p:first-child');
            const links = [];
            hazardNameElements.forEach(p => {
                const name = p.innerText;
                const descriptionSibling = p.nextElementSibling;
                if (name && name.trim() !== '' && descriptionSibling && descriptionSibling.tagName === 'P' && descriptionSibling.classList.contains('MuiTypography-body1')) {
                    const potentialHref = '/hazards/' + name.trim().toLowerCase().replace(/ /g, '-').replace(/\//g, '-');
                    links.push({ href: 'https://app.hazadapt.com' + potentialHref, text: name.trim() });
                }
            });
            return links;
        }''')
        
        # Deduplicate based on href
        unique_links = {link['href']: link['text'] for link in links}
        
        print(f"Found {len(unique_links)} hazards.")
        
        count = 0
        for href, text in unique_links.items():
            if limit and count >= limit:
                break
                
            # Clean text
            name = text.split('\n')[0].strip()
            if not name:
                name = href.split('/')[-1]
                
            await scrape_hazard(page, href, name)
            count += 1
            
        await browser.close()

def scrape_hazards(limit=None):
    asyncio.run(scrape_hazards_async(limit))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Hazadapt Hazards")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of hazards to scrape")
    args = parser.parse_args()
    scrape_hazards(args.limit)
