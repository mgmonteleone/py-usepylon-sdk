#!/usr/bin/env python3
"""
Pylon Knowledge Base Scraper CLI

Scrapes articles from Pylon's public knowledge base and exports to various formats.
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from .kb_scraper import PylonKBScraper, export_to_json, export_to_csv, export_to_html

# ASCII Art Logo
LOGO = r"""
    ___                                  __     ______          __
   /   |  __  ______ _____ ___  ___  ____/ /_   / ____/___  ____/ /__
  / /| | / / / / __ `/ __ `__ \/ _ \/ __  __/  / /   / __ \/ __  / _ \
 / ___ |/ /_/ / /_/ / / / / / /  __/ / / /_   / /___/ /_/ / /_/ /  __/
/_/  |_|\__,_/\__, /_/ /_/ /_/\___/_/ \__/   \____/\____/\__,_/\___/
             /____/
"""


def main():
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description='Scrape Pylon Knowledge Base articles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all articles and export to JSON
  python scrape_knowledge_base.py --json articles.json
  
  # Scrape and export to all formats
  python scrape_knowledge_base.py --all
  
  # Scrape with custom delay between requests
  python scrape_knowledge_base.py --json articles.json --delay 2.0
  
  # Use custom knowledge base URL
  python scrape_knowledge_base.py --json articles.json --kb-url https://support.example.com
        """
    )
    
    parser.add_argument(
        '--json',
        type=str,
        help='Export to JSON file'
    )
    
    parser.add_argument(
        '--csv',
        type=str,
        help='Export to CSV file'
    )
    
    parser.add_argument(
        '--html',
        type=str,
        help='Export to HTML file'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Export to all formats (JSON, CSV, HTML)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay in seconds between requests (default: 1.0)'
    )
    
    parser.add_argument(
        '--kb-url',
        type=str,
        default='https://support.augmentcode.com',
        help='Knowledge base URL (default: https://support.augmentcode.com)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Pylon API key (default: from PYLON_API_KEY env var)'
    )
    
    args = parser.parse_args()
    
    # Print logo
    print('\033[94m' + LOGO + '\033[0m')
    print('🔍 Pylon Knowledge Base Scraper')
    print('=' * 80)
    print()
    
    # Get API key
    api_key = args.api_key or os.getenv('PYLON_API_KEY')
    if not api_key:
        print('❌ Error: PYLON_API_KEY not found in environment variables')
        print('   Set it in .env file or pass --api-key argument')
        sys.exit(1)
    
    # Check if at least one export format is specified
    if not (args.json or args.csv or args.html or args.all):
        print('❌ Error: Please specify at least one export format')
        print('   Use --json, --csv, --html, or --all')
        print()
        parser.print_help()
        sys.exit(1)
    
    # Initialize scraper
    print(f'🌐 Knowledge Base URL: {args.kb_url}')
    print(f'⏱️  Delay between requests: {args.delay}s')
    print()
    
    scraper = PylonKBScraper(api_key=api_key, kb_base_url=args.kb_url)
    
    # Scrape all articles
    try:
        articles = scraper.scrape_all_articles(delay_seconds=args.delay)
    except Exception as e:
        print(f'\n❌ Error during scraping: {e}')
        sys.exit(1)
    
    if not articles:
        print('⚠️  No articles found!')
        sys.exit(0)
    
    print()
    print('=' * 80)
    print('📦 Exporting articles...')
    print()
    
    # Export to requested formats
    if args.all or args.json:
        json_file = args.json or 'pylon_kb_articles.json'
        export_to_json(articles, json_file)
    
    if args.all or args.csv:
        csv_file = args.csv or 'pylon_kb_articles.csv'
        export_to_csv(articles, csv_file)
    
    if args.all or args.html:
        html_file = args.html or 'pylon_kb_articles.html'
        export_to_html(articles, html_file, title='Augment Code Knowledge Base')
    
    print()
    print('=' * 80)
    print('✅ Done!')
    print()


if __name__ == '__main__':
    main()

