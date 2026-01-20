"""Unit tests for filter builder utilities.

Tests for the filters module including Field, And, Or, Not classes
and operator overloading.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from pylon.filters import And, Field, FieldFilter, Not, Or


class TestFieldFilter:
    """Tests for FieldFilter class."""

    def test_to_dict_basic(self) -> None:
        """Test FieldFilter serializes correctly."""
        f = FieldFilter("status", "eq", "open")
        assert f.to_dict() == {
            "field": "status",
            "operator": "eq",
            "value": "open",
        }

    def test_to_dict_with_list_value(self) -> None:
        """Test FieldFilter with list value."""
        f = FieldFilter("status", "in", ["open", "pending"])
        assert f.to_dict() == {
            "field": "status",
            "operator": "in",
            "value": ["open", "pending"],
        }


class TestFieldBuilder:
    """Tests for Field builder class."""

    def test_eq_creates_equality_filter(self) -> None:
        """Test eq() creates equality filter."""
        f = Field("state").eq("open")
        assert f.to_dict() == {
            "field": "state",
            "operator": "eq",
            "value": "open",
        }

    def test_neq_creates_inequality_filter(self) -> None:
        """Test neq() creates inequality filter."""
        f = Field("state").neq("closed")
        assert f.to_dict() == {
            "field": "state",
            "operator": "neq",
            "value": "closed",
        }

    def test_in_creates_in_list_filter(self) -> None:
        """Test in_() creates in-list filter."""
        f = Field("status").in_(["open", "pending"])
        assert f.to_dict() == {
            "field": "status",
            "operator": "in",
            "value": ["open", "pending"],
        }

    def test_not_in_creates_not_in_filter(self) -> None:
        """Test not_in() creates not-in-list filter."""
        f = Field("status").not_in(["closed", "archived"])
        assert f.to_dict() == {
            "field": "status",
            "operator": "not_in",
            "value": ["closed", "archived"],
        }

    def test_gt_creates_greater_than_filter(self) -> None:
        """Test gt() creates greater-than filter."""
        f = Field("priority").gt(3)
        assert f.to_dict() == {
            "field": "priority",
            "operator": "gt",
            "value": 3,
        }

    def test_gte_creates_greater_equal_filter(self) -> None:
        """Test gte() creates greater-than-or-equal filter."""
        f = Field("priority").gte(3)
        assert f.to_dict() == {
            "field": "priority",
            "operator": "gte",
            "value": 3,
        }

    def test_lt_creates_less_than_filter(self) -> None:
        """Test lt() creates less-than filter."""
        f = Field("priority").lt(5)
        assert f.to_dict() == {
            "field": "priority",
            "operator": "lt",
            "value": 5,
        }

    def test_lte_creates_less_equal_filter(self) -> None:
        """Test lte() creates less-than-or-equal filter."""
        f = Field("priority").lte(5)
        assert f.to_dict() == {
            "field": "priority",
            "operator": "lte",
            "value": 5,
        }

    def test_contains_creates_substring_filter(self) -> None:
        """Test contains() creates substring filter."""
        f = Field("title").contains("urgent")
        assert f.to_dict() == {
            "field": "title",
            "operator": "contains",
            "value": "urgent",
        }

    def test_starts_with_creates_prefix_filter(self) -> None:
        """Test starts_with() creates prefix filter."""
        f = Field("title").starts_with("[BUG]")
        assert f.to_dict() == {
            "field": "title",
            "operator": "starts_with",
            "value": "[BUG]",
        }

    def test_ends_with_creates_suffix_filter(self) -> None:
        """Test ends_with() creates suffix filter."""
        f = Field("email").ends_with("@example.com")
        assert f.to_dict() == {
            "field": "email",
            "operator": "ends_with",
            "value": "@example.com",
        }

    def test_after_creates_datetime_filter(self) -> None:
        """Test after() creates datetime filter with ISO format."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        f = Field("created_at").after(dt)
        assert f.to_dict() == {
            "field": "created_at",
            "operator": "gt",
            "value": "2024-01-15T10:30:00",
        }

    def test_before_creates_datetime_filter(self) -> None:
        """Test before() creates datetime filter with ISO format."""
        dt = datetime(2024, 12, 31, 23, 59, 59)
        f = Field("created_at").before(dt)
        assert f.to_dict() == {
            "field": "created_at",
            "operator": "lt",
            "value": "2024-12-31T23:59:59",
        }

    def test_between_creates_and_filter(self) -> None:
        """Test between() creates And filter with gte and lte."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        f = Field("created_at").between(start, end)

        assert isinstance(f, And)
        result = f.to_dict()
        assert "and" in result
        assert len(result["and"]) == 2

    def test_is_null_creates_null_check(self) -> None:
        """Test is_null() creates null check filter."""
        f = Field("assignee_id").is_null()
        assert f.to_dict() == {
            "field": "assignee_id",
            "operator": "is_null",
            "value": True,
        }

    def test_is_not_null_creates_not_null_check(self) -> None:
        """Test is_not_null() creates not-null check filter."""
        f = Field("assignee_id").is_not_null()
        assert f.to_dict() == {
            "field": "assignee_id",
            "operator": "is_null",
            "value": False,
        }


class TestAndFilter:
    """Tests for And filter class."""

    def test_and_requires_at_least_two_filters(self) -> None:
        """Test And raises error with fewer than 2 filters."""
        with pytest.raises(ValueError) as exc_info:
            And(Field("state").eq("open"))

        assert "at least 2" in str(exc_info.value)

    def test_and_combines_two_filters(self) -> None:
        """Test And combines two filters correctly."""
        f = And(
            Field("state").eq("open"),
            Field("priority").gte(3),
        )

        result = f.to_dict()
        assert "and" in result
        assert len(result["and"]) == 2
        assert result["and"][0]["field"] == "state"
        assert result["and"][1]["field"] == "priority"

    def test_and_combines_multiple_filters(self) -> None:
        """Test And combines multiple filters."""
        f = And(
            Field("state").eq("open"),
            Field("priority").gte(3),
            Field("team").eq("support"),
        )

        result = f.to_dict()
        assert len(result["and"]) == 3


class TestOrFilter:
    """Tests for Or filter class."""

    def test_or_requires_at_least_two_filters(self) -> None:
        """Test Or raises error with fewer than 2 filters."""
        with pytest.raises(ValueError) as exc_info:
            Or(Field("state").eq("open"))

        assert "at least 2" in str(exc_info.value)

    def test_or_combines_two_filters(self) -> None:
        """Test Or combines two filters correctly."""
        f = Or(
            Field("state").eq("open"),
            Field("state").eq("pending"),
        )

        result = f.to_dict()
        assert "or" in result
        assert len(result["or"]) == 2


class TestNotFilter:
    """Tests for Not filter class."""

    def test_not_negates_filter(self) -> None:
        """Test Not negates a filter."""
        f = Not(Field("state").eq("closed"))

        result = f.to_dict()
        assert "not" in result
        assert result["not"]["field"] == "state"
        assert result["not"]["value"] == "closed"


class TestOperatorOverloading:
    """Tests for operator overloading (&, |, ~)."""

    def test_and_operator(self) -> None:
        """Test & operator creates And filter."""
        f = Field("state").eq("open") & Field("priority").gte(3)

        assert isinstance(f, And)
        result = f.to_dict()
        assert "and" in result

    def test_or_operator(self) -> None:
        """Test | operator creates Or filter."""
        f = Field("state").eq("open") | Field("state").eq("pending")

        assert isinstance(f, Or)
        result = f.to_dict()
        assert "or" in result

    def test_invert_operator(self) -> None:
        """Test ~ operator creates Not filter."""
        f = ~Field("state").eq("closed")

        assert isinstance(f, Not)
        result = f.to_dict()
        assert "not" in result

    def test_complex_combination(self) -> None:
        """Test complex filter combination."""
        f = (Field("state").eq("open") | Field("state").eq("pending")) & ~Field(
            "priority"
        ).lt(3)

        result = f.to_dict()
        assert "and" in result
        # First part is Or
        assert "or" in result["and"][0]
        # Second part is Not
        assert "not" in result["and"][1]

