"""
Pylon API Client Library

This library provides a Python interface to the Pylon API for reading
customer support data including issues, messages, tags, and attachments.

It also includes utilities for working with knowledge base content from
Markdown files, since Pylon does not expose a Knowledge Base API.
"""

try:
    # PylonClient depends on optional external HTTP libraries (e.g. ``requests``).
    # Import it lazily so that modules which only need the webhook/event models
    # can still be imported in minimal environments (such as unit tests) where
    # those dependencies may not be installed.
    from .client import PylonClient
except ImportError:  # pragma: no cover - exercised when optional deps are missing
    PylonClient = None  # type: ignore[assignment]
from .knowledge_base import (
    KnowledgeArticle,
    get_statistics,
    parse_faq_markdown,
)
from .knowledge_base import (
    export_to_csv as export_markdown_to_csv,
)
from .knowledge_base import (
    export_to_html as export_markdown_to_html,
)
from .knowledge_base import (
    export_to_json as export_markdown_to_json,
)
from .models import (
    PylonAccount,
    PylonAttachment,
    PylonContact,
    PylonIssue,
    PylonMessage,
    PylonTag,
    PylonTeam,
    PylonUser,
)
from .webhook_events import (
    BaseIssueEvent,
    IssueAssignedEvent,
    IssueFieldChangedEvent,
    IssueMessageNewEvent,
    IssueNewEvent,
    IssueReactionEvent,
    IssueSnapshotEvent,
    IssueStatusChangedEvent,
    IssueTagsChangedEvent,
    PylonWebhookEvent,
    parse_webhook_event,
)

# kb_scraper requires playwright which is a heavy optional dependency
# Import it lazily so that modules which don't need it can still be imported
try:
    from .kb_scraper import (
        PylonKBScraper,
        ScrapedArticle,
    )
    from .kb_scraper import (
        export_to_csv as export_scraped_to_csv,
    )
    from .kb_scraper import (
        export_to_html as export_scraped_to_html,
    )
    from .kb_scraper import (
        export_to_json as export_scraped_to_json,
    )
except ImportError:  # pragma: no cover - exercised when playwright is not installed
    PylonKBScraper = None  # type: ignore[assignment]
    ScrapedArticle = None  # type: ignore[assignment]
    export_scraped_to_json = None  # type: ignore[assignment]
    export_scraped_to_csv = None  # type: ignore[assignment]
    export_scraped_to_html = None  # type: ignore[assignment]

__all__ = [
    # API Client
    'PylonClient',
    # API Models
    'PylonIssue',
    'PylonMessage',
    'PylonTag',
    'PylonAttachment',
    'PylonAccount',
    'PylonContact',
    'PylonUser',
    'PylonTeam',
    # Webhook Event Models
    'BaseIssueEvent',
    'IssueSnapshotEvent',
    'IssueNewEvent',
    'IssueAssignedEvent',
    'IssueFieldChangedEvent',
    'IssueStatusChangedEvent',
    'IssueTagsChangedEvent',
    'IssueReactionEvent',
    'IssueMessageNewEvent',
    'PylonWebhookEvent',
    'parse_webhook_event',
    # Knowledge Base (Markdown)
    'KnowledgeArticle',
    'parse_faq_markdown',
    'export_markdown_to_json',
    'export_markdown_to_csv',
    'export_markdown_to_html',
    'get_statistics',
    # Knowledge Base (Web Scraper)
    'PylonKBScraper',
    'ScrapedArticle',
    'export_scraped_to_json',
    'export_scraped_to_csv',
    'export_scraped_to_html',
]
