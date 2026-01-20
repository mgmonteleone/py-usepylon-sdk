"""Unit tests for the exception hierarchy."""

import pytest

from pylon.exceptions import (
    PylonAPIError,
    PylonAuthenticationError,
    PylonError,
    PylonNotFoundError,
    PylonRateLimitError,
    PylonServerError,
    PylonValidationError,
)


class TestPylonError:
    """Tests for the base PylonError."""

    def test_base_error_inherits_from_exception(self):
        """PylonError should inherit from Exception."""
        assert issubclass(PylonError, Exception)

    def test_base_error_can_be_raised(self):
        """PylonError should be raisable."""
        with pytest.raises(PylonError):
            raise PylonError("test error")


class TestPylonAPIError:
    """Tests for PylonAPIError."""

    def test_inherits_from_pylon_error(self):
        """PylonAPIError should inherit from PylonError."""
        assert issubclass(PylonAPIError, PylonError)

    def test_stores_status_code_and_message(self):
        """PylonAPIError should store status code and message."""
        error = PylonAPIError(status_code=500, message="Internal error")
        assert error.status_code == 500
        assert error.message == "Internal error"
        assert error.request_id is None

    def test_stores_request_id(self):
        """PylonAPIError should store optional request ID."""
        error = PylonAPIError(status_code=500, message="Error", request_id="req_123")
        assert error.request_id == "req_123"

    def test_str_representation(self):
        """PylonAPIError should have a useful string representation."""
        error = PylonAPIError(status_code=500, message="Internal error")
        assert str(error) == "[500] Internal error"


class TestPylonAuthenticationError:
    """Tests for PylonAuthenticationError."""

    def test_inherits_from_api_error(self):
        """PylonAuthenticationError should inherit from PylonAPIError."""
        assert issubclass(PylonAuthenticationError, PylonAPIError)

    def test_default_status_code_is_401(self):
        """PylonAuthenticationError should have status code 401."""
        error = PylonAuthenticationError()
        assert error.status_code == 401

    def test_default_message(self):
        """PylonAuthenticationError should have default message."""
        error = PylonAuthenticationError()
        assert error.message == "Authentication failed"


class TestPylonRateLimitError:
    """Tests for PylonRateLimitError."""

    def test_inherits_from_api_error(self):
        """PylonRateLimitError should inherit from PylonAPIError."""
        assert issubclass(PylonRateLimitError, PylonAPIError)

    def test_default_status_code_is_429(self):
        """PylonRateLimitError should have status code 429."""
        error = PylonRateLimitError()
        assert error.status_code == 429

    def test_stores_retry_after(self):
        """PylonRateLimitError should store retry_after."""
        error = PylonRateLimitError(retry_after=60)
        assert error.retry_after == 60


class TestPylonNotFoundError:
    """Tests for PylonNotFoundError."""

    def test_inherits_from_api_error(self):
        """PylonNotFoundError should inherit from PylonAPIError."""
        assert issubclass(PylonNotFoundError, PylonAPIError)

    def test_default_status_code_is_404(self):
        """PylonNotFoundError should have status code 404."""
        error = PylonNotFoundError()
        assert error.status_code == 404


class TestPylonValidationError:
    """Tests for PylonValidationError."""

    def test_inherits_from_api_error(self):
        """PylonValidationError should inherit from PylonAPIError."""
        assert issubclass(PylonValidationError, PylonAPIError)

    def test_default_status_code_is_400(self):
        """PylonValidationError should have status code 400."""
        error = PylonValidationError()
        assert error.status_code == 400

    def test_stores_errors_list(self):
        """PylonValidationError should store validation errors."""
        errors = [{"field": "name", "message": "required"}]
        error = PylonValidationError(errors=errors)
        assert error.errors == errors

    def test_default_errors_is_empty_list(self):
        """PylonValidationError should have empty errors by default."""
        error = PylonValidationError()
        assert error.errors == []


class TestPylonServerError:
    """Tests for PylonServerError."""

    def test_inherits_from_api_error(self):
        """PylonServerError should inherit from PylonAPIError."""
        assert issubclass(PylonServerError, PylonAPIError)

    def test_default_status_code_is_500(self):
        """PylonServerError should have status code 500."""
        error = PylonServerError()
        assert error.status_code == 500

    def test_custom_status_code(self):
        """PylonServerError should accept custom 5xx status codes."""
        error = PylonServerError(status_code=502)
        assert error.status_code == 502
