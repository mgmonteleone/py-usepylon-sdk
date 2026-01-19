# Pylon API Client Library (`pylonlib`)

A comprehensive Python library for interacting with the Pylon API and working with knowledge base content.

## 🎯 Features

### Pylon API Client
- ✅ Full Pylon API integration with type-safe Pydantic models
- ✅ Support for Issues, Messages, Tags, Attachments, Accounts, Contacts, Users, Teams
- ✅ Automatic retry logic with exponential backoff
- ✅ Rate limiting and error handling
- ✅ Pagination support for large datasets
- ✅ Search and filtering capabilities

### Knowledge Base Module (Markdown)
- ✅ Parse FAQ Markdown files into structured articles
- ✅ Export to multiple formats (JSON, CSV, HTML)
- ✅ Rich HTML export with styling and table of contents
- ✅ Support for categories, tags, and metadata
- ✅ Detect internal-only and incomplete articles
- ✅ Standalone CLI tool
- ✅ Statistics and reporting

### Knowledge Base Web Scraper (NEW!)
- ✅ Scrape articles from Pylon's public knowledge base pages
- ✅ Merge scraped content with API collection metadata
- ✅ Uses Playwright for JavaScript-rendered pages
- ✅ Export to JSON, CSV, and HTML
- ✅ Configurable rate limiting
- ✅ Beautiful CLI with progress tracking
- ✅ Handles 40+ articles automatically

## 📦 Installation

### Core Dependencies

```bash
pip install requests pydantic tenacity python-dotenv markdown beautifulsoup4
```

### Additional Dependencies for Web Scraper

```bash
pip install playwright
python -m playwright install chromium
```

### As a Standalone Module

Simply copy the entire `pylonlib/` directory to your project:

```bash
cp -r pylonlib /path/to/your/project/
```

## 🚀 Quick Start

### Pylon API Client

```python
from pylonlib import PylonClient

# Initialize client (uses PYLON_API_KEY environment variable)
client = PylonClient()

# Get all accounts
accounts = list(client.get_accounts())
print(f"Found {len(accounts)} accounts")

# Get issues for the last 30 days
issues = list(client.get_issues(days=30))
print(f"Found {len(issues)} issues")

# Search issues by account
account_issues = list(client.search_issues_by_account(account_id="acc_123"))

# Get messages for an issue
messages = list(client.get_messages(issue_id="iss_456"))
```

### Knowledge Base Module

```python
from pylonlib import (
    parse_faq_markdown,
    export_to_json,
    export_to_csv,
    export_to_html,
    get_statistics
)

# Parse FAQ markdown file
articles = parse_faq_markdown('reference/FAQ.md')

# Get statistics
stats = get_statistics(articles)
print(f"Total articles: {stats['total_articles']}")

# Export to various formats
export_to_json(articles, 'knowledge_base.json')
export_to_csv(articles, 'knowledge_base.csv')
export_to_html(articles, 'knowledge_base.html', title='My Knowledge Base')
```

### Knowledge Base Web Scraper

```python
from pylonlib import PylonKBScraper, export_scraped_to_json
import os

# Initialize scraper
scraper = PylonKBScraper(
    api_key=os.getenv('PYLON_API_KEY'),
    kb_base_url='https://support.augmentcode.com'
)

# Scrape all articles
articles = scraper.scrape_all_articles(delay_seconds=1.0)

# Export to JSON
export_scraped_to_json(articles, 'scraped_articles.json')

print(f"Scraped {len(articles)} articles!")
```

### CLI Tools

#### Markdown Knowledge Base Export

```bash
# Export knowledge base to all formats
cd pylonlib
python export_knowledge_base.py ../reference/FAQ.md --all

# Show statistics only
python export_knowledge_base.py ../reference/FAQ.md --stats

# Export to specific format
python export_knowledge_base.py ../reference/FAQ.md --json output.json
```

#### Web Scraper

```bash
# Scrape all articles and export to JSON
cd pylonlib
python scrape_knowledge_base.py --json articles.json

# Export to all formats
python scrape_knowledge_base.py --all

# Custom delay between requests
python scrape_knowledge_base.py --json articles.json --delay 2.0
```

## 📚 Documentation

### Module Structure

```
pylonlib/
├── __init__.py                 # Main module exports
├── client.py                   # Pylon API client
├── models.py                   # Pydantic models for API entities
├── knowledge_base.py           # Knowledge base parsing and export (Markdown)
├── kb_scraper.py               # Knowledge base web scraper (NEW!)
├── export_knowledge_base.py    # CLI tool for Markdown KB export
├── scrape_knowledge_base.py    # CLI tool for web scraping (NEW!)
├── README.md                   # This file
├── KB_SCRAPER_README.md        # Web scraper documentation (NEW!)
├── KNOWLEDGE_BASE_README.md    # Detailed knowledge base documentation
└── examples/
    └── knowledge_base_example.py  # Example usage
```

### API Models

All API responses are parsed into type-safe Pydantic models:

- `PylonIssue` - Support tickets/conversations
- `PylonMessage` - Comments on issues
- `PylonTag` - Tags for categorization
- `PylonAttachment` - File attachments
- `PylonAccount` - Customer accounts
- `PylonContact` - Customer contacts
- `PylonUser` - Pylon users (support agents)
- `PylonTeam` - Support teams
- `KnowledgeArticle` - Knowledge base articles

### Environment Variables

```bash
# Required for Pylon API client
PYLON_API_KEY=your_pylon_api_key_here
```

## 📖 Examples

### Example 1: Fetch All Issues for an Account

```python
from pylonlib import PylonClient

client = PylonClient()

# Get account by name
accounts = [acc for acc in client.get_accounts() if acc.name == "Acme Corp"]
if accounts:
    account = accounts[0]
    
    # Get all issues for this account
    issues = list(client.search_issues_by_account(account_id=account.id))
    
    print(f"Found {len(issues)} issues for {account.name}")
    for issue in issues:
        print(f"  - {issue.title} (Status: {issue.status})")
```

### Example 2: Export Knowledge Base

```python
from pylonlib import parse_faq_markdown, export_to_html, get_statistics

# Parse FAQ
articles = parse_faq_markdown('FAQ.md')

# Get stats
stats = get_statistics(articles)
print(f"Categories: {list(stats['categories'].keys())}")

# Export to beautiful HTML
export_to_html(articles, 'knowledge_base.html', title='Support KB')
```

### Example 3: Create Custom Knowledge Article

```python
from pylonlib import KnowledgeArticle

article = KnowledgeArticle.from_markdown(
    title="How to install?",
    question="How do I install the software?",
    answer_markdown="""
    Follow these steps:
    
    1. Download the installer
    2. Run the installer
    3. Follow the prompts
    """,
    category="Installation",
    tags=["setup", "getting-started"]
)

print(f"URL Name: {article.url_name}")
print(f"HTML: {article.answer_html}")
```

## 🔧 Advanced Usage

### Custom Retry Logic

```python
from pylonlib import PylonClient

client = PylonClient(api_key="your_key")

# The client automatically retries failed requests with exponential backoff
# Default: 5 attempts, 4-60 second delays
```

### Pagination

```python
# The client handles pagination automatically
# All get_* methods return iterators that fetch pages as needed

for issue in client.get_issues(days=90):
    # Process each issue
    # Pages are fetched automatically in the background
    print(issue.title)
```

### Search with Filters

```python
# Search issues with complex filters
issues = client.search_issues_by_account(
    account_id="acc_123",
    # Additional filters can be added via the API
)
```

## 📝 Knowledge Base Markdown Format

The knowledge base parser expects this format:

```markdown
# Category Name

### Question 1?

Answer content in markdown...

### Question 2?

More answer content...
```

### Special Markers

- `🔵` or "internal only" - Marks article as internal
- `🟡` or "incomplete" - Marks article as incomplete
- `[tag1] [tag2]` - Add tags to question title

## 🎨 HTML Export Features

The HTML export creates a beautiful, responsive page with:

- 📚 Table of contents with category links
- 🎨 Modern gradient header
- 📱 Responsive design
- 🏷️ Badge indicators for internal/incomplete articles
- 💅 Syntax highlighting for code blocks
- 🔗 External links open in new tabs

## 🔄 Copying to Another Project

To use this library in another project:

1. **Copy the directory:**
   ```bash
   cp -r pylonlib /path/to/your/project/
   ```

2. **Install dependencies:**
   ```bash
   pip install requests pydantic tenacity python-dotenv markdown beautifulsoup4
   ```

3. **Set environment variables:**
   ```bash
   export PYLON_API_KEY=your_api_key
   ```

4. **Import and use:**
   ```python
   from pylonlib import PylonClient, parse_faq_markdown
   
   client = PylonClient()
   articles = parse_faq_markdown('FAQ.md')
   ```

## 📄 License

Part of the Augment Code internal tools.

## 🤝 Contributing

This is an internal library. For questions or issues, contact the Support & Customer Success team.

## 📚 Additional Documentation

- [Knowledge Base Module Documentation](KNOWLEDGE_BASE_README.md) - Detailed docs for knowledge base features
- [Examples](examples/) - Example scripts demonstrating usage

## ✨ What's Included

- ✅ Complete Pylon API client with all endpoints
- ✅ Type-safe Pydantic models
- ✅ Knowledge base parsing and export
- ✅ CLI tool for knowledge base export
- ✅ Example scripts
- ✅ Comprehensive documentation
- ✅ Ready to copy to other projects

