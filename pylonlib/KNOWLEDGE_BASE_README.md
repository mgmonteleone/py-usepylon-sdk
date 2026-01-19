# Pylon Knowledge Base Module

This module provides utilities for working with knowledge base content from Markdown files.

**Note:** Pylon's Knowledge Base API supports **creating** and **updating** articles, but does **NOT** support reading/listing existing articles (returns 403 "Not available"). Therefore, this module works with local Markdown documentation files for export purposes.

## Features

- ✅ Parse FAQ Markdown files into structured articles
- ✅ Export to multiple formats (JSON, CSV, HTML)
- ✅ Rich HTML export with styling and table of contents
- ✅ Pydantic models for type safety
- ✅ Support for categories, tags, and metadata
- ✅ Detect internal-only and incomplete articles
- ✅ Generate URL-friendly names
- ✅ Convert Markdown to HTML and plain text
- ✅ Standalone CLI tool
- ✅ Statistics and reporting

## Installation

The module is part of the `pylonlib` package. Make sure you have the required dependencies:

```bash
pip install pydantic markdown beautifulsoup4
```

## Usage

### As a Python Module

```python
from pylonlib import (
    parse_faq_markdown,
    export_to_json,
    export_to_csv,
    export_to_html,
    get_statistics,
    KnowledgeArticle
)

# Parse FAQ markdown file
articles = parse_faq_markdown('reference/FAQ.md')

# Get statistics
stats = get_statistics(articles)
print(f"Total articles: {stats['total_articles']}")
print(f"Categories: {stats['categories']}")

# Export to JSON
export_to_json(articles, 'knowledge_base.json')

# Export to CSV
export_to_csv(articles, 'knowledge_base.csv')

# Export to HTML
export_to_html(articles, 'knowledge_base.html', title='My Knowledge Base')

# Work with individual articles
for article in articles:
    print(f"Title: {article.title}")
    print(f"Category: {article.category}")
    print(f"URL Name: {article.url_name}")
    print(f"HTML: {article.answer_html}")
    print(f"Plain Text: {article.answer_plain}")
```

### As a CLI Tool

```bash
# Navigate to pylonlib directory
cd pylonlib

# Export to JSON
python export_knowledge_base.py ../reference/FAQ.md --json knowledge_base.json

# Export to CSV
python export_knowledge_base.py ../reference/FAQ.md --csv knowledge_base.csv

# Export to HTML
python export_knowledge_base.py ../reference/FAQ.md --html knowledge_base.html --title "Augment Knowledge Base"

# Export to all formats
python export_knowledge_base.py ../reference/FAQ.md --all

# Show statistics only
python export_knowledge_base.py ../reference/FAQ.md --stats
```

## Markdown Format

The parser expects Markdown files in this format:

```markdown
# Category Name

### Question 1?

Answer content in markdown...

### Question 2?

More answer content...

# Another Category

### Question 3?

Even more content...
```

### Special Markers

- **Internal Only**: Include 🔵 emoji or "internal only" text to mark as internal
- **Incomplete**: Include 🟡 emoji, ❓ emoji, or "incomplete" text to mark as incomplete
- **Tags**: Include `[tag1] [tag2]` in the question title

### Example

```markdown
# General

### What is Augment?

Augment is a developer AI platform that helps you understand code, debug issues,
and ship faster because it understands your codebase.

### [Setup] How do I install Augment? 🟡

Installation instructions coming soon...

### [Internal] How do we handle enterprise contracts? 🔵

Internal process for enterprise sales...
```

## KnowledgeArticle Model

```python
class KnowledgeArticle(BaseModel):
    title: str                          # Article title
    category: str                       # Category (from H1)
    subcategory: Optional[str]          # Subcategory (optional)
    question: str                       # The question
    answer_markdown: str                # Answer in Markdown
    answer_html: str                    # Answer in HTML
    answer_plain: str                   # Answer in plain text
    tags: List[str]                     # Tags/keywords
    is_internal_only: bool              # Internal only flag
    is_incomplete: bool                 # Incomplete flag
    url_name: str                       # URL-friendly name
    created_at: Optional[datetime]      # Creation date
    updated_at: Optional[datetime]      # Last update date
```

## Export Formats

### JSON

Structured JSON with metadata:

```json
{
  "exported_at": "2025-11-11T10:30:00",
  "total_articles": 50,
  "articles": [
    {
      "title": "What is Augment?",
      "category": "General",
      "question": "What is Augment?",
      "answer_markdown": "...",
      "answer_html": "...",
      "answer_plain": "...",
      "tags": [],
      "is_internal_only": false,
      "is_incomplete": false,
      "url_name": "What-is-Augment"
    }
  ]
}
```

### CSV

Flat CSV format suitable for spreadsheets:

```csv
title,category,subcategory,question,answer_markdown,answer_html,answer_plain,tags,is_internal_only,is_incomplete,url_name
"What is Augment?","General",,"What is Augment?","...","...","...",,false,false,"What-is-Augment"
```

### HTML

Beautiful, styled HTML page with:
- Table of contents
- Category grouping
- Syntax highlighting
- Responsive design
- Badge indicators for internal/incomplete articles

## Statistics

Get comprehensive statistics about your knowledge base:

```python
stats = get_statistics(articles)

# Returns:
{
    'total_articles': 50,
    'categories': {'General': 10, 'Setup': 15, ...},
    'tags': {'setup': 5, 'troubleshooting': 3, ...},
    'internal_only_count': 5,
    'incomplete_count': 8,
    'complete_public_count': 37
}
```

## Integration with Other Systems

### Salesforce Knowledge

While Salesforce Knowledge requires a paid license, the module includes a helper method:

```python
article = KnowledgeArticle.from_markdown(...)
salesforce_data = article.to_salesforce_dict()
# Returns dict ready for Salesforce Knowledge__kav object
```

### Zendesk

Export to JSON or CSV and import into Zendesk Guide using their API or bulk import tools.

### Custom Systems

Use the JSON export as a data source for any custom knowledge base system.

## Copying to Another Project

To use this module in another project:

1. Copy the entire `pylonlib/` directory
2. Install dependencies: `pip install pydantic markdown beautifulsoup4`
3. Import and use:

```python
from pylonlib import parse_faq_markdown, export_to_json

articles = parse_faq_markdown('path/to/FAQ.md')
export_to_json(articles, 'output.json')
```

## License

Part of the Augment Code internal tools.

