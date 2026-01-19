#!/usr/bin/env python3
"""
Pylon Knowledge Base Export CLI

This script exports knowledge base content from Markdown files to various formats.

Usage:
    python export_knowledge_base.py <input_file> [options]
    
Examples:
    # Export to JSON
    python export_knowledge_base.py reference/FAQ.md --json knowledge_base.json
    
    # Export to CSV
    python export_knowledge_base.py reference/FAQ.md --csv knowledge_base.csv
    
    # Export to HTML
    python export_knowledge_base.py reference/FAQ.md --html knowledge_base.html
    
    # Export to all formats
    python export_knowledge_base.py reference/FAQ.md --all
    
    # Show statistics only
    python export_knowledge_base.py reference/FAQ.md --stats
"""

import sys
import argparse
from pathlib import Path

from .knowledge_base import (
    parse_faq_markdown,
    export_to_json,
    export_to_csv,
    export_to_html,
    get_statistics,
)


def print_logo():
    """Print ASCII art logo."""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     █████╗ ██╗   ██╗ ██████╗ ███╗   ███╗███████╗███╗   ██╗  ║
    ║    ██╔══██╗██║   ██║██╔════╝ ████╗ ████║██╔════╝████╗  ██║  ║
    ║    ███████║██║   ██║██║  ███╗██╔████╔██║█████╗  ██╔██╗ ██║  ║
    ║    ██╔══██║██║   ██║██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║  ║
    ║    ██║  ██║╚██████╔╝╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║  ║
    ║    ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝  ║
    ║                                                               ║
    ║              Knowledge Base Export Tool                       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)


def print_statistics(stats: dict):
    """Print knowledge base statistics."""
    print("\n" + "=" * 80)
    print("📊 KNOWLEDGE BASE STATISTICS")
    print("=" * 80)
    print(f"\n📚 Total Articles: {stats['total_articles']}")
    print(f"✅ Complete & Public: {stats['complete_public_count']}")
    print(f"🔵 Internal Only: {stats['internal_only_count']}")
    print(f"🟡 Incomplete: {stats['incomplete_count']}")
    
    print(f"\n📂 Articles by Category:")
    for category, count in stats['categories'].items():
        print(f"   {category:40} {count:3} articles")
    
    if stats['tags']:
        print(f"\n🏷️  Top Tags:")
        for tag, count in list(stats['tags'].items())[:10]:
            print(f"   {tag:40} {count:3} articles")
    
    print("\n" + "=" * 80)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Export Pylon knowledge base content from Markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'input_file',
        help='Path to input Markdown file (e.g., reference/FAQ.md)'
    )
    
    parser.add_argument(
        '--json',
        metavar='FILE',
        help='Export to JSON file'
    )
    
    parser.add_argument(
        '--csv',
        metavar='FILE',
        help='Export to CSV file'
    )
    
    parser.add_argument(
        '--html',
        metavar='FILE',
        help='Export to HTML file'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Export to all formats (JSON, CSV, HTML) with default names'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics only (no export)'
    )
    
    parser.add_argument(
        '--title',
        default='Knowledge Base',
        help='Title for HTML export (default: "Knowledge Base")'
    )
    
    parser.add_argument(
        '--no-logo',
        action='store_true',
        help='Suppress ASCII art logo'
    )
    
    args = parser.parse_args()
    
    # Print logo
    if not args.no_logo:
        print_logo()
    
    # Check input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Parse articles
    print(f"\n📖 Parsing {args.input_file}...")
    try:
        articles = parse_faq_markdown(str(input_path))
        print(f"✅ Parsed {len(articles)} articles")
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        sys.exit(1)
    
    # Get statistics
    stats = get_statistics(articles)
    
    # Show statistics if requested
    if args.stats or not (args.json or args.csv or args.html or args.all):
        print_statistics(stats)
    
    # Export to formats
    if args.all:
        # Export to all formats with default names
        base_name = input_path.stem
        export_to_json(articles, f"{base_name}.json")
        export_to_csv(articles, f"{base_name}.csv")
        export_to_html(articles, f"{base_name}.html", title=args.title)
    else:
        if args.json:
            export_to_json(articles, args.json)
        if args.csv:
            export_to_csv(articles, args.csv)
        if args.html:
            export_to_html(articles, args.html, title=args.title)
    
    print("\n✅ Export complete!\n")


if __name__ == '__main__':
    main()

