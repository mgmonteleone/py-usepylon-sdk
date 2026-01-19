"""
Pylon Knowledge Base Module

This module provides utilities for working with knowledge base content.
Since Pylon does not expose a Knowledge Base API, this module provides
tools to parse and export knowledge base content from Markdown files.

Usage:
    from pylonlib.knowledge_base import KnowledgeArticle, parse_faq_markdown, export_to_json
    
    # Parse FAQ markdown file
    articles = parse_faq_markdown('reference/FAQ.md')
    
    # Export to JSON
    export_to_json(articles, 'knowledge_base.json')
    
    # Export to CSV
    export_to_csv(articles, 'knowledge_base.csv')
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import re
import markdown
from bs4 import BeautifulSoup


class KnowledgeArticle(BaseModel):
    """
    Represents a knowledge base article.
    
    Attributes:
        title: Article title (usually the question)
        category: Article category (from H1/H2 headings)
        subcategory: Article subcategory (optional)
        question: The question being answered
        answer_markdown: Answer content in Markdown format
        answer_html: Answer content in HTML format
        answer_plain: Answer content in plain text
        tags: List of tags/keywords
        is_internal_only: Whether article is for internal use only
        is_incomplete: Whether article is marked as incomplete
        url_name: URL-friendly name for the article
        created_at: When the article was created (if available)
        updated_at: When the article was last updated (if available)
    """
    
    title: str
    category: str
    subcategory: Optional[str] = None
    question: str
    answer_markdown: str
    answer_html: str
    answer_plain: str
    tags: List[str] = Field(default_factory=list)
    is_internal_only: bool = False
    is_incomplete: bool = False
    url_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @staticmethod
    def markdown_to_html(md_text: str) -> str:
        """Convert Markdown to HTML."""
        html = markdown.markdown(
            md_text,
            extensions=['extra', 'nl2br', 'sane_lists', 'tables', 'fenced_code']
        )
        # Add security attributes to links
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            link['target'] = '_blank'
            link['rel'] = 'noopener noreferrer'
        return str(soup)
    
    @staticmethod
    def html_to_plain(html_text: str) -> str:
        """Convert HTML to plain text."""
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    
    @staticmethod
    def generate_url_name(title: str) -> str:
        """Generate URL-friendly name from title."""
        # Remove special characters, replace spaces with hyphens
        url_name = re.sub(r'[^\w\s-]', '', title)
        url_name = re.sub(r'[\s_]+', '-', url_name)
        url_name = url_name.strip('-')
        return url_name[:255]  # Limit to 255 chars
    
    @classmethod
    def from_markdown(
        cls,
        title: str,
        question: str,
        answer_markdown: str,
        category: str,
        subcategory: Optional[str] = None,
        is_internal_only: bool = False,
        is_incomplete: bool = False,
        tags: Optional[List[str]] = None
    ) -> "KnowledgeArticle":
        """
        Create a KnowledgeArticle from Markdown content.
        
        Args:
            title: Article title
            question: The question being answered
            answer_markdown: Answer in Markdown format
            category: Article category
            subcategory: Article subcategory (optional)
            is_internal_only: Whether article is internal only
            is_incomplete: Whether article is incomplete
            tags: List of tags
        
        Returns:
            KnowledgeArticle instance
        """
        answer_html = cls.markdown_to_html(answer_markdown)
        answer_plain = cls.html_to_plain(answer_html)
        url_name = cls.generate_url_name(title)
        
        return cls(
            title=title,
            category=category,
            subcategory=subcategory,
            question=question,
            answer_markdown=answer_markdown,
            answer_html=answer_html,
            answer_plain=answer_plain,
            tags=tags or [],
            is_internal_only=is_internal_only,
            is_incomplete=is_incomplete,
            url_name=url_name
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()
    
    def to_salesforce_dict(self) -> Dict[str, Any]:
        """
        Convert to Salesforce Knowledge__kav format.

        Note: This requires Salesforce Knowledge license.
        """
        return {
            'Title': self.title[:255],
            'UrlName': self.url_name,
            'Summary': self.answer_plain[:1000],
            'Content__c': self.answer_html[:32768],
            'Question__c': self.markdown_to_html(self.question)[:32768],
            'Language': 'en_US',
            'IsVisibleInApp': True,
            'IsVisibleInCsp': not self.is_internal_only,
            'IsVisibleInPkb': False,
            'IsVisibleInPrm': False
        }


def parse_faq_markdown(file_path: str) -> List[KnowledgeArticle]:
    """
    Parse a FAQ Markdown file and extract knowledge articles.

    Expected format:
        # Category Name

        ### Question?

        Answer content in markdown...

        ### Another Question?

        More answer content...

    Args:
        file_path: Path to the Markdown file

    Returns:
        List of KnowledgeArticle objects
    """
    articles = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by H1 headings (categories)
    category_sections = re.split(r'^# (.+)$', content, flags=re.MULTILINE)

    # First element is content before first H1 (usually empty)
    category_sections = category_sections[1:]

    # Process pairs of (category_name, category_content)
    for i in range(0, len(category_sections), 2):
        if i + 1 >= len(category_sections):
            break

        category = category_sections[i].strip()
        category_content = category_sections[i + 1]

        # Split by H3 headings (questions)
        question_sections = re.split(r'^### (.+)$', category_content, flags=re.MULTILINE)

        # First element is content before first H3 (usually empty or intro text)
        question_sections = question_sections[1:]

        # Process pairs of (question, answer)
        for j in range(0, len(question_sections), 2):
            if j + 1 >= len(question_sections):
                break

            question = question_sections[j].strip()
            answer = question_sections[j + 1].strip()

            # Skip empty answers
            if not answer:
                continue

            # Check for special markers
            is_internal_only = '🔵' in answer or 'internal only' in answer.lower()
            is_incomplete = '🟡' in answer or 'incomplete' in answer.lower() or '❓' in answer

            # Extract tags from question (if any)
            tags = []
            if '[' in question and ']' in question:
                tag_match = re.findall(r'\[([^\]]+)\]', question)
                tags = [tag.strip() for tag in tag_match]
                # Remove tags from question
                question = re.sub(r'\[([^\]]+)\]', '', question).strip()

            # Create article
            article = KnowledgeArticle.from_markdown(
                title=question,
                question=question,
                answer_markdown=answer,
                category=category,
                is_internal_only=is_internal_only,
                is_incomplete=is_incomplete,
                tags=tags
            )

            articles.append(article)

    return articles


def export_to_json(articles: List[KnowledgeArticle], output_path: str, indent: int = 2) -> None:
    """
    Export articles to JSON format.

    Args:
        articles: List of KnowledgeArticle objects
        output_path: Path to output JSON file
        indent: JSON indentation (default: 2)
    """
    import json

    data = {
        'exported_at': datetime.now().isoformat(),
        'total_articles': len(articles),
        'articles': [article.to_dict() for article in articles]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

    print(f'✅ Exported {len(articles)} articles to {output_path}')


def export_to_csv(articles: List[KnowledgeArticle], output_path: str) -> None:
    """
    Export articles to CSV format.

    Args:
        articles: List of KnowledgeArticle objects
        output_path: Path to output CSV file
    """
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        if not articles:
            return

        fieldnames = [
            'title', 'category', 'subcategory', 'question',
            'answer_markdown', 'answer_html', 'answer_plain',
            'tags', 'is_internal_only', 'is_incomplete', 'url_name'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for article in articles:
            row = article.to_dict()
            # Convert list to comma-separated string
            row['tags'] = ', '.join(row['tags'])
            # Only include specified fields
            row = {k: v for k, v in row.items() if k in fieldnames}
            writer.writerow(row)

    print(f'✅ Exported {len(articles)} articles to {output_path}')


def export_to_html(articles: List[KnowledgeArticle], output_path: str, title: str = "Knowledge Base") -> None:
    """
    Export articles to a single HTML file.

    Args:
        articles: List of KnowledgeArticle objects
        output_path: Path to output HTML file
        title: HTML page title
    """
    html_parts = [
        f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .stats {{
            margin-top: 10px;
            opacity: 0.9;
        }}
        .category {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .category-title {{
            font-size: 2em;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .article {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}
        .article-title {{
            font-size: 1.3em;
            color: #333;
            margin-bottom: 10px;
        }}
        .article-meta {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 15px;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-right: 5px;
        }}
        .badge-internal {{
            background: #ffc107;
            color: #000;
        }}
        .badge-incomplete {{
            background: #ff9800;
            color: white;
        }}
        .badge-tag {{
            background: #e0e0e0;
            color: #333;
        }}
        .article-content {{
            color: #444;
        }}
        .article-content a {{
            color: #667eea;
            text-decoration: none;
        }}
        .article-content a:hover {{
            text-decoration: underline;
        }}
        .article-content code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
        }}
        .article-content pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .toc {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .toc h2 {{
            margin-top: 0;
            color: #667eea;
        }}
        .toc ul {{
            list-style: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 5px 0;
        }}
        .toc a {{
            color: #333;
            text-decoration: none;
        }}
        .toc a:hover {{
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="stats">
            {len(articles)} articles • Exported {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </div>
    </div>
'''
    ]

    # Group articles by category
    categories: Dict[str, List[KnowledgeArticle]] = {}
    for article in articles:
        if article.category not in categories:
            categories[article.category] = []
        categories[article.category].append(article)

    # Table of contents
    html_parts.append('    <div class="toc">\n        <h2>📚 Table of Contents</h2>\n        <ul>\n')
    for category in sorted(categories.keys()):
        category_id = re.sub(r'[^\w-]', '', category.replace(' ', '-')).lower()
        html_parts.append(f'            <li><a href="#{category_id}">{category}</a> ({len(categories[category])} articles)</li>\n')
    html_parts.append('        </ul>\n    </div>\n\n')

    # Articles by category
    for category in sorted(categories.keys()):
        category_id = re.sub(r'[^\w-]', '', category.replace(' ', '-')).lower()
        html_parts.append(f'    <div class="category" id="{category_id}">\n')
        html_parts.append(f'        <h2 class="category-title">{category}</h2>\n')

        for article in categories[category]:
            html_parts.append('        <div class="article">\n')
            html_parts.append(f'            <h3 class="article-title">{article.title}</h3>\n')

            # Meta badges
            if article.is_internal_only or article.is_incomplete or article.tags:
                html_parts.append('            <div class="article-meta">\n')
                if article.is_internal_only:
                    html_parts.append('                <span class="badge badge-internal">🔵 Internal Only</span>\n')
                if article.is_incomplete:
                    html_parts.append('                <span class="badge badge-incomplete">🟡 Incomplete</span>\n')
                for tag in article.tags:
                    html_parts.append(f'                <span class="badge badge-tag">{tag}</span>\n')
                html_parts.append('            </div>\n')

            html_parts.append(f'            <div class="article-content">\n                {article.answer_html}\n            </div>\n')
            html_parts.append('        </div>\n')

        html_parts.append('    </div>\n\n')

    html_parts.append('</body>\n</html>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))

    print(f'✅ Exported {len(articles)} articles to {output_path}')


def get_statistics(articles: List[KnowledgeArticle]) -> Dict[str, Any]:
    """
    Get statistics about the knowledge base articles.

    Args:
        articles: List of KnowledgeArticle objects

    Returns:
        Dictionary with statistics
    """
    categories: Dict[str, int] = {}
    tags: Dict[str, int] = {}
    internal_count = 0
    incomplete_count = 0

    for article in articles:
        # Count by category
        categories[article.category] = categories.get(article.category, 0) + 1

        # Count tags
        for tag in article.tags:
            tags[tag] = tags.get(tag, 0) + 1

        # Count flags
        if article.is_internal_only:
            internal_count += 1
        if article.is_incomplete:
            incomplete_count += 1

    return {
        'total_articles': len(articles),
        'categories': dict(sorted(categories.items())),
        'tags': dict(sorted(tags.items(), key=lambda x: x[1], reverse=True)),
        'internal_only_count': internal_count,
        'incomplete_count': incomplete_count,
        'complete_public_count': len(articles) - internal_count - incomplete_count
    }

