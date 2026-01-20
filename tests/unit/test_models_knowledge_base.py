"""Unit tests for knowledge base models."""

from pylon.models import PylonKnowledgeBase, PylonKnowledgeBaseArticle


class TestPylonKnowledgeBase:
    """Tests for PylonKnowledgeBase model."""

    def test_from_pylon_dict_minimal(self):
        """Should create knowledge base with minimal fields."""
        data = {
            "id": "kb_123",
            "name": "Help Center",
        }
        kb = PylonKnowledgeBase.from_pylon_dict(data)
        assert kb.id == "kb_123"
        assert kb.name == "Help Center"
        assert kb.description is None
        assert kb.article_count == 0

    def test_from_pylon_dict_full(self):
        """Should create knowledge base with all fields."""
        data = {
            "id": "kb_456",
            "name": "Product Documentation",
            "description": "Complete product documentation",
            "article_count": 50,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-03-20T15:30:00Z",
        }
        kb = PylonKnowledgeBase.from_pylon_dict(data)
        assert kb.id == "kb_456"
        assert kb.name == "Product Documentation"
        assert kb.description == "Complete product documentation"
        assert kb.article_count == 50
        # Check datetime values (may be timezone-aware)
        assert kb.created_at is not None
        assert kb.created_at.year == 2024
        assert kb.created_at.month == 1
        assert kb.updated_at is not None
        assert kb.updated_at.year == 2024
        assert kb.updated_at.month == 3


class TestPylonKnowledgeBaseArticle:
    """Tests for PylonKnowledgeBaseArticle model."""

    def test_from_pylon_dict_minimal(self):
        """Should create article with minimal fields."""
        data = {
            "id": "article_123",
            "title": "Getting Started",
            "knowledge_base_id": "kb_456",
        }
        article = PylonKnowledgeBaseArticle.from_pylon_dict(data)
        assert article.id == "article_123"
        assert article.title == "Getting Started"
        assert article.knowledge_base_id == "kb_456"
        assert article.status == "draft"
        assert article.view_count == 0

    def test_from_pylon_dict_full(self):
        """Should create article with all fields."""
        data = {
            "id": "article_789",
            "title": "Advanced Configuration",
            "content": "# Advanced Configuration\n\nThis guide covers...",
            "knowledge_base_id": "kb_456",
            "status": "published",
            "created_at": "2024-02-01T09:00:00Z",
            "updated_at": "2024-02-15T14:00:00Z",
            "author_id": "user_123",
            "view_count": 1500,
        }
        article = PylonKnowledgeBaseArticle.from_pylon_dict(data)
        assert article.id == "article_789"
        assert article.title == "Advanced Configuration"
        assert article.content is not None
        assert "Advanced Configuration" in article.content
        assert article.status == "published"
        assert article.author_id == "user_123"
        assert article.view_count == 1500
        # Check datetime values (may be timezone-aware)
        assert article.created_at is not None
        assert article.created_at.year == 2024
        assert article.created_at.month == 2
        assert article.updated_at is not None
        assert article.updated_at.year == 2024

    def test_extra_fields_ignored(self):
        """Should ignore unknown fields."""
        data = {
            "id": "article_extra",
            "title": "Test Article",
            "knowledge_base_id": "kb_789",
            "unknown_field": "should be ignored",
        }
        article = PylonKnowledgeBaseArticle.from_pylon_dict(data)
        assert article.id == "article_extra"
        assert not hasattr(article, "unknown_field")
