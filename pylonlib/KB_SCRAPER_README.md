# Pylon Knowledge Base Web Scraper

This module provides functionality to scrape knowledge base articles from Pylon's public knowledge base pages and merge them with collection metadata from the Pylon API.

## Why Web Scraping?

Pylon's Knowledge Base API has **limited read access**:
- ✅ Can GET knowledge bases and collections
- ✅ Can CREATE and UPDATE articles
- ❌ **Cannot LIST or READ existing articles** (returns 403 "Not available")

Therefore, we use web scraping to extract article content from the public knowledge base pages, then merge it with collection metadata from the API.

---

## Features

- 🌐 **Web Scraping** - Uses Playwright to scrape JavaScript-rendered pages
- 📡 **API Integration** - Merges scraped content with Pylon API collection metadata
- 📦 **Multiple Export Formats** - JSON, CSV, and HTML
- ⏱️ **Rate Limiting** - Configurable delay between requests
- 🎨 **Beautiful CLI** - Colored output with ASCII art logo
- 🔄 **Idempotent** - Safe to run multiple times

---

## Installation

The scraper requires Playwright for web scraping:

```bash
# Install Python dependencies
pip install playwright beautifulsoup4 lxml

# Install Playwright browsers
python -m playwright install chromium
```

---

## Quick Start

### Command Line Usage

```bash
# Scrape all articles and export to JSON
cd pylonlib
python scrape_knowledge_base.py --json articles.json

# Export to all formats
python scrape_knowledge_base.py --all

# Custom delay between requests (to avoid rate limiting)
python scrape_knowledge_base.py --json articles.json --delay 2.0

# Custom knowledge base URL
python scrape_knowledge_base.py --json articles.json --kb-url https://support.example.com
```

### Python API Usage

```python
from dotenv import load_dotenv
import os
from pylonlib import PylonKBScraper, export_scraped_to_json

load_dotenv()

# Initialize scraper
scraper = PylonKBScraper(
    api_key=os.getenv('PYLON_API_KEY'),
    kb_base_url='https://support.augmentcode.com'
)

# Scrape all articles
articles = scraper.scrape_all_articles(delay_seconds=1.0)

# Export to JSON
export_scraped_to_json(articles, 'articles.json')

print(f"Scraped {len(articles)} articles!")
```

---

## How It Works

### 1. Get Collections from API

```python
collections = scraper.get_collections_from_api()
# Returns: [{'id': '...', 'title': 'FAQs', 'slug': 'faqs', ...}, ...]
```

### 2. Scrape Homepage for Links

```python
homepage_data = scraper.scrape_homepage()
# Returns: {
#   'collections': [{'title': 'FAQs', 'url': 'https://...'}],
#   'articles': [{'title': 'How to...', 'url': 'https://...'}]
# }
```

### 3. Scrape Each Collection Page

```python
articles = scraper.scrape_collection('https://support.augmentcode.com/collections/...')
# Returns: [{'title': 'Article 1', 'url': 'https://...'}, ...]
```

### 4. Scrape Individual Articles

```python
article = scraper.scrape_article('https://support.augmentcode.com/articles/...')
# Returns: ScrapedArticle(
#   url='https://...',
#   title='How to install Augment?',
#   body_html='<p>...</p>',
#   body_text='Installation instructions...',
#   collection_id='...',
#   collection_title='Setup & Installation'
# )
```

### 5. Merge API Metadata with Scraped Content

The scraper automatically matches collection URLs with API data by slug, enriching scraped articles with:
- Collection ID from API
- Collection metadata
- Proper categorization

---

## Data Model

### ScrapedArticle

```python
class ScrapedArticle(BaseModel):
    url: str                          # Article URL
    title: str                        # Article title
    body_html: str                    # Full HTML content
    body_text: str                    # Plain text content
    collection_id: Optional[str]      # Collection ID from API
    collection_title: Optional[str]   # Collection title
    slug: Optional[str]               # Article slug from URL
    created_at: Optional[datetime]    # Creation timestamp (if available)
    updated_at: Optional[datetime]    # Update timestamp (if available)
```

---

## Export Formats

### JSON Export

```json
{
  "exported_at": "2025-11-11T10:30:00",
  "total_articles": 42,
  "articles": [
    {
      "url": "https://support.augmentcode.com/articles/...",
      "title": "How to install Augment?",
      "body_html": "<p>Installation instructions...</p>",
      "body_text": "Installation instructions...",
      "collection_id": "19b19384-8742-442e-869f-c9f20a5de374",
      "collection_title": "Setup & Installation",
      "slug": "how-to-install-augment"
    }
  ]
}
```

### CSV Export

Columns:
- Title
- URL
- Collection
- Collection ID
- Slug
- Body Text (Preview)
- Body HTML Length

### HTML Export

Single-page HTML file with:
- Table of contents
- Articles grouped by collection
- Styled with CSS
- Links to original articles

---

## CLI Options

```
usage: scrape_knowledge_base.py [-h] [--json JSON] [--csv CSV] [--html HTML]
                                 [--all] [--delay DELAY] [--kb-url KB_URL]
                                 [--api-key API_KEY]

options:
  -h, --help         show this help message and exit
  --json JSON        Export to JSON file
  --csv CSV          Export to CSV file
  --html HTML        Export to HTML file
  --all              Export to all formats (JSON, CSV, HTML)
  --delay DELAY      Delay in seconds between requests (default: 1.0)
  --kb-url KB_URL    Knowledge base URL (default: https://support.augmentcode.com)
  --api-key API_KEY  Pylon API key (default: from PYLON_API_KEY env var)
```

---

## Example Output

```
🔍 Pylon Knowledge Base Scraper
================================================================================

🌐 Knowledge Base URL: https://support.augmentcode.com
⏱️  Delay between requests: 1.0s

🔍 Getting collections from API...
   Found 7 collections from API

🌐 Scraping homepage for article links...
   Found 6 collection links
   Found 5 article links on homepage

📁 Scraping collections for articles...
   FAQs...
      Found 4 articles
   Setup & Installation...
      Found 4 articles
   Features & Usage...
      Found 6 articles

📄 Scraping 42 unique articles...
   [1/42] What is Augment Code?...
   [2/42] How do I install Augment?...
   ...

✅ Successfully scraped 42 articles!

================================================================================
📦 Exporting articles...

✅ Exported 42 articles to articles.json

================================================================================
✅ Done!
```

---

## Best Practices

1. **Use Appropriate Delays** - Set `--delay` to 1-2 seconds to avoid overwhelming the server
2. **Run During Off-Peak Hours** - Minimize impact on live knowledge base
3. **Cache Results** - Save scraped data to avoid re-scraping
4. **Handle Errors Gracefully** - The scraper continues even if individual articles fail
5. **Respect robots.txt** - Check the knowledge base's robots.txt file

---

## Troubleshooting

### Playwright Timeout Errors

If you get timeout errors, try:
- Increasing the timeout in `kb_scraper.py`
- Checking your internet connection
- Verifying the knowledge base URL is accessible

### Missing Articles

If articles are missing:
- Check if they're published and public
- Verify the collection URLs are correct
- Increase the wait time after page load

### Rate Limiting

If you're being rate limited:
- Increase `--delay` to 2-3 seconds
- Run the scraper during off-peak hours
- Contact Pylon support for guidance

---

## Future Enhancements

Potential improvements:
- [ ] Incremental scraping (only new/updated articles)
- [ ] Parallel scraping with thread pool
- [ ] Article metadata extraction (author, dates, tags)
- [ ] Support for article attachments/images
- [ ] Automatic retry on failures
- [ ] Progress bar for long scraping sessions

---

## Related Files

- `kb_scraper.py` - Core scraper module
- `scrape_knowledge_base.py` - CLI tool
- `knowledge_base.py` - Markdown-based KB module (alternative approach)
- `PYLON_KNOWLEDGE_BASE_API_FINDINGS.md` - API research findings

