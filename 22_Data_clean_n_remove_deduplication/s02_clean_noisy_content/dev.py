
# Clean "Noisy" Content: Remove irrelevant boilerplate such as headers, footers,
#       navigation menus from web scrapes, and special characters that don't add semantic value.

# Why:  Improves Retrieval Accuracy
#       Reduces Costs & Latency
#       Prevents Hallucinations
#       Optimizes Embedding Quality

import json
from trafilatura import fetch_url, extract
from trafilatura import extract_metadata
from playwright.sync_api import sync_playwright

# url = 'https://www.nzpostbusinessiq.co.nz/annual-ecommerce-review'
# url = 'https://theiconic.co.nz/mens-clothing-tops-all/?page=1&sort=popularity'
url = 'https://en.wikipedia.org/wiki/Large_language_model'
downloaded_html = fetch_url(url)

if not downloaded_html:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        downloaded_html=page.content()
        browser.close()

if downloaded_html:
    noise_free_result = extract(filecontent=downloaded_html, output_format="json", with_metadata=True)
    print("===============================")
    print(json.dumps(noise_free_result, indent=4))
    print("===============================")
    metadata = extract_metadata(downloaded_html)
    if metadata:
        print(f"Title : {metadata.title}")
        print(f"Author: {metadata.author}")
        print(f"Date  : {metadata.date}")

# verify elements in header and footer manually 1st then programmatically

