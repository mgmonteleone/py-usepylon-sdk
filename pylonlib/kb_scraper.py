#!/usr/bin/env python3
"""
Pylon Knowledge Base Scraper

This module scrapes knowledge base articles from Pylon's public knowledge base pages
and merges them with collection metadata from the Pylon API.

Since Pylon's API doesn't support reading articles, we use web scraping to get the content.
"""

import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pydantic import BaseModel


class ScrapedArticle(BaseModel):
    """Scraped knowledge base article"""

    url: str
    title: str
    body_html: str
    body_text: str
    collection_id: str | None = None
    collection_title: str | None = None
    slug: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class PylonKBScraper:
    """
    Scraper for Pylon Knowledge Base

    Combines API metadata with web-scraped article content.
    """

    def __init__(
        self, api_key: str, kb_base_url: str = "https://support.augmentcode.com"
    ):
        """
        Initialize the scraper

        Args:
            api_key: Pylon API key
            kb_base_url: Base URL of the knowledge base (default: https://support.augmentcode.com)
        """
        self.api_key = api_key
        self.kb_base_url = kb_base_url.rstrip("/")
        self.kb_id = "405c5b71-bfd3-4ad6-9d65-d915546452c7"  # Augment Code KB ID

    def get_collections_from_api(self) -> list[dict]:
        """Get collections from Pylon API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"https://api.usepylon.com/knowledge-bases/{self.kb_id}/collections",
            headers=headers,
        )

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            raise Exception(
                f"Failed to get collections: {response.status_code} - {response.text}"
            )

    def scrape_homepage(self) -> dict[str, list[dict]]:
        """
        Scrape the knowledge base homepage to find collection and article links

        Returns:
            Dict with 'collections' and 'articles' lists
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(
                    self.kb_base_url, wait_until="domcontentloaded", timeout=60000
                )
                page.wait_for_timeout(5000)  # Wait for JS to render

                html = page.content()
            finally:
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=True)

            article_links = []
            collection_links = []

            for link in links:
                href = link.get("href", "")
                text = link.get_text(strip=True)

                if not text:  # Skip empty links
                    continue

                if "/articles/" in href or "/a/" in href:
                    full_url = (
                        href if href.startswith("http") else f"{self.kb_base_url}{href}"
                    )
                    article_links.append({"title": text, "url": full_url})
                elif "/collections/" in href or "/c/" in href:
                    full_url = (
                        href if href.startswith("http") else f"{self.kb_base_url}{href}"
                    )
                    collection_links.append({"title": text, "url": full_url})

            return {"collections": collection_links, "articles": article_links}

    def scrape_collection(self, collection_url: str) -> list[dict]:
        """
        Scrape a collection page to find all articles in that collection

        Args:
            collection_url: URL of the collection page

        Returns:
            List of article dicts with 'title' and 'url'
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(collection_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)

                html = page.content()
            finally:
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=True)

            articles = []
            for link in links:
                href = link.get("href", "")
                text = link.get_text(strip=True)

                if text and ("/articles/" in href or "/a/" in href):
                    full_url = (
                        href if href.startswith("http") else f"{self.kb_base_url}{href}"
                    )
                    articles.append({"title": text, "url": full_url})

            return articles

    def scrape_article(
        self,
        url: str,
        collection_id: str | None = None,
        collection_title: str | None = None,
    ) -> ScrapedArticle:
        """
        Scrape a single article

        Args:
            url: URL of the article
            collection_id: Optional collection ID from API
            collection_title: Optional collection title

        Returns:
            ScrapedArticle object
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)

                html = page.content()
            finally:
                browser.close()

            soup = BeautifulSoup(html, "html.parser")

            # Extract title
            title_elem = soup.find("h1")
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            # Extract article body (try multiple selectors)
            body = (
                soup.find("article")
                or soup.find(class_="article-body")
                or soup.find(class_="content")
                or soup.find(class_="article-content")
                or soup.find("main")
            )

            body_html = str(body) if body else ""
            body_text = body.get_text(strip=True) if body else ""

            # Extract slug from URL
            slug = url.split("/")[-1] if "/" in url else None

            return ScrapedArticle(
                url=url,
                title=title,
                body_html=body_html,
                body_text=body_text,
                collection_id=collection_id,
                collection_title=collection_title,
                slug=slug,
            )

    def scrape_all_articles(self, delay_seconds: float = 1.0) -> list[ScrapedArticle]:
        """
        Scrape all articles from the knowledge base

        Args:
            delay_seconds: Delay between requests to avoid rate limiting

        Returns:
            List of ScrapedArticle objects
        """
        print("🔍 Getting collections from API...")
        api_collections = self.get_collections_from_api()
        print(f"   Found {len(api_collections)} collections from API\n")

        print("🌐 Scraping homepage for article links...")
        homepage_data = self.scrape_homepage()
        print(f"   Found {len(homepage_data['collections'])} collection links")
        print(f"   Found {len(homepage_data['articles'])} article links on homepage\n")

        # Create a mapping of collection URLs to API data
        collection_map = {}
        for api_coll in api_collections:
            # Try to match by slug
            for web_coll in homepage_data["collections"]:
                if api_coll["slug"] in web_coll["url"]:
                    collection_map[web_coll["url"]] = api_coll
                    break

        # Scrape all collections to get article lists
        all_articles = []
        article_urls_seen = set()

        print("📁 Scraping collections for articles...")
        for web_coll in homepage_data["collections"]:
            api_coll = collection_map.get(web_coll["url"])
            coll_id = api_coll["id"] if api_coll else None
            coll_title = web_coll["title"]

            print(f"   {coll_title}...")
            articles_in_coll = self.scrape_collection(web_coll["url"])
            print(f"      Found {len(articles_in_coll)} articles")

            for article_info in articles_in_coll:
                if article_info["url"] not in article_urls_seen:
                    article_urls_seen.add(article_info["url"])
                    all_articles.append(
                        {
                            "url": article_info["url"],
                            "title": article_info["title"],
                            "collection_id": coll_id,
                            "collection_title": coll_title,
                        }
                    )

            time.sleep(delay_seconds)

        print(f"\n📄 Scraping {len(all_articles)} unique articles...")
        scraped_articles = []

        for i, article_info in enumerate(all_articles, 1):
            print(f"   [{i}/{len(all_articles)}] {article_info['title'][:60]}...")

            try:
                scraped = self.scrape_article(
                    article_info["url"],
                    article_info.get("collection_id"),
                    article_info.get("collection_title"),
                )
                scraped_articles.append(scraped)
            except Exception as e:
                print(f"      ⚠️  Error: {str(e)[:100]}")

            time.sleep(delay_seconds)

        print(f"\n✅ Successfully scraped {len(scraped_articles)} articles!")
        return scraped_articles


def export_to_json(articles: list[ScrapedArticle], output_file: str) -> None:
    """Export scraped articles to JSON"""
    import json

    data = {
        "exported_at": datetime.now().isoformat(),
        "total_articles": len(articles),
        "articles": [article.model_dump() for article in articles],
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Exported {len(articles)} articles to {output_file}")


def export_to_csv(articles: list[ScrapedArticle], output_file: str) -> None:
    """Export scraped articles to CSV"""
    import csv

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Title",
                "URL",
                "Collection",
                "Collection ID",
                "Slug",
                "Body Text (Preview)",
                "Body HTML Length",
            ]
        )

        for article in articles:
            writer.writerow(
                [
                    article.title,
                    article.url,
                    article.collection_title or "",
                    article.collection_id or "",
                    article.slug or "",
                    article.body_text[:500] + "..."
                    if len(article.body_text) > 500
                    else article.body_text,
                    len(article.body_html),
                ]
            )

    print(f"✅ Exported {len(articles)} articles to {output_file}")


def export_to_html(
    articles: list[ScrapedArticle],
    output_file: str,
    title: str = "Knowledge Base Articles",
) -> None:
    """Export scraped articles to a single HTML file"""

    # Group by collection
    by_collection = {}
    for article in articles:
        coll = article.collection_title or "Uncategorized"
        if coll not in by_collection:
            by_collection[coll] = []
        by_collection[coll].append(article)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 40px; }}
        h3 {{ color: #7f8c8d; }}
        .article {{ margin: 20px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #3498db; }}
        .article-title {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .article-meta {{ font-size: 0.9em; color: #7f8c8d; margin-bottom: 15px; }}
        .article-body {{ margin-top: 15px; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .toc {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .toc ul {{ list-style: none; padding-left: 20px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Exported on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p><strong>Total Articles:</strong> {len(articles)}</p>

    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
"""

    for collection in sorted(by_collection.keys()):
        html += f'            <li><a href="#{collection.replace(" ", "-")}">{collection}</a> ({len(by_collection[collection])} articles)</li>\n'

    html += """        </ul>
    </div>
"""

    for collection in sorted(by_collection.keys()):
        html += f'\n    <h2 id="{collection.replace(" ", "-")}">{collection}</h2>\n'

        for article in by_collection[collection]:
            html += f"""
    <div class="article">
        <h3 class="article-title">{article.title}</h3>
        <div class="article-meta">
            <a href="{article.url}" target="_blank">View Original</a>
            {f" | Collection: {article.collection_title}" if article.collection_title else ""}
        </div>
        <div class="article-body">
            {article.body_html}
        </div>
    </div>
"""

    html += """
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Exported {len(articles)} articles to {output_file}")
