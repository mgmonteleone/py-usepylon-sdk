# Pylon Library - Quick Start Guide

## 🚀 Copy to Another Project

### 1. Copy the Directory

```bash
cp -r pylonlib /path/to/your/project/
```

### 2. Install Dependencies

```bash
pip install requests pydantic tenacity python-dotenv markdown beautifulsoup4
```

### 3. Set Environment Variable

```bash
export PYLON_API_KEY=your_api_key_here
```

Or create `.env` file:
```
PYLON_API_KEY=your_api_key_here
```

### 4. Use It!

```python
from pylonlib import PylonClient, parse_faq_markdown

# Pylon API
client = PylonClient()
issues = list(client.get_issues(days=30))

# Knowledge Base
articles = parse_faq_markdown('FAQ.md')
```

---

## 📚 Common Use Cases

### Get All Issues for an Account

```python
from pylonlib import PylonClient

client = PylonClient()
issues = list(client.search_issues_by_account(account_id="acc_123"))
print(f"Found {len(issues)} issues")
```

### Export Knowledge Base to HTML

```python
from pylonlib import parse_faq_markdown, export_to_html

articles = parse_faq_markdown('FAQ.md')
export_to_html(articles, 'knowledge_base.html', title='Support KB')
```

### Get Statistics

```python
from pylonlib import parse_faq_markdown, get_statistics

articles = parse_faq_markdown('FAQ.md')
stats = get_statistics(articles)
print(f"Total: {stats['total_articles']}")
print(f"Categories: {stats['categories']}")
```

### CLI Tool

```bash
cd pylonlib
python export_knowledge_base.py ../FAQ.md --all
```

---

## 📖 Full Documentation

- [README.md](README.md) - Complete module documentation
- [KNOWLEDGE_BASE_README.md](KNOWLEDGE_BASE_README.md) - Knowledge base details
- [examples/](examples/) - Example scripts

---

## ✅ What's Included

- ✅ Pylon API client with all endpoints
- ✅ Type-safe Pydantic models
- ✅ Knowledge base parsing (Markdown → JSON/CSV/HTML)
- ✅ CLI tool for exports
- ✅ Automatic retry logic
- ✅ Error handling
- ✅ Pagination support
- ✅ Examples and documentation

---

## 🎯 Module Exports

```python
# API Client
from pylonlib import PylonClient

# API Models
from pylonlib import (
    PylonIssue,
    PylonMessage,
    PylonTag,
    PylonAttachment,
    PylonAccount,
    PylonContact,
    PylonUser,
    PylonTeam,
)

# Knowledge Base
from pylonlib import (
    KnowledgeArticle,
    parse_faq_markdown,
    export_to_json,
    export_to_csv,
    export_to_html,
    get_statistics,
)
```

---

## 🔧 Dependencies

```
requests>=2.31.0
pydantic>=2.0.0
tenacity>=8.2.0
python-dotenv>=1.0.0
markdown>=3.10
beautifulsoup4>=4.14.0
```

---

## 📞 Support

For questions, contact the Support & Customer Success team.

**Version:** 1.0.0  
**Last Updated:** 2025-11-11

