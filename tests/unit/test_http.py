"""Unit tests for HTTP transport layer."""

import httpx
import pytest
import respx

from pylon._http import AsyncHTTPTransport, SyncHTTPTransport
from pylon.exceptions import (
    PylonAuthenticationError,
    PylonNotFoundError,
    PylonRateLimitError,
    PylonServerError,
    PylonValidationError,
)


class TestSyncHTTPTransport:
    """Tests for synchronous HTTP transport."""

    def test_creates_with_defaults(self):
        """Should create transport with default settings."""
        transport = SyncHTTPTransport(api_key="test-key")
        assert transport.base_url == "https://api.usepylon.com"
        assert transport.timeout == 30.0
        assert transport.max_retries == 3
        transport.close()

    def test_custom_settings(self):
        """Should accept custom settings."""
        transport = SyncHTTPTransport(
            api_key="test-key",
            base_url="https://custom.api.com",
            timeout=60.0,
            max_retries=5,
        )
        assert transport.base_url == "https://custom.api.com"
        assert transport.timeout == 60.0
        assert transport.max_retries == 5
        transport.close()

    @respx.mock
    def test_get_request(self):
        """Should make GET requests."""
        respx.get("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(200, json={"data": "value"})
        )

        transport = SyncHTTPTransport(api_key="test-key")
        response = transport.request("GET", "/test")
        assert response == {"data": "value"}
        transport.close()

    @respx.mock
    def test_post_request(self):
        """Should make POST requests with JSON body."""
        respx.post("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(201, json={"id": "new_123"})
        )

        transport = SyncHTTPTransport(api_key="test-key")
        response = transport.request("POST", "/test", json={"name": "test"})
        assert response == {"id": "new_123"}
        transport.close()

    @respx.mock
    def test_authentication_error(self):
        """Should raise PylonAuthenticationError on 401."""
        respx.get("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(
                401, json={"error": {"message": "Unauthorized"}}
            )
        )

        transport = SyncHTTPTransport(api_key="bad-key")
        with pytest.raises(PylonAuthenticationError):
            transport.request("GET", "/test")
        transport.close()

    @respx.mock
    def test_not_found_error(self):
        """Should raise PylonNotFoundError on 404."""
        respx.get("https://api.usepylon.com/notfound").mock(
            return_value=httpx.Response(404, json={"error": {"message": "Not found"}})
        )

        transport = SyncHTTPTransport(api_key="test-key")
        with pytest.raises(PylonNotFoundError):
            transport.request("GET", "/notfound")
        transport.close()

    @respx.mock
    def test_rate_limit_error(self):
        """Should raise PylonRateLimitError on 429."""
        respx.get("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(429, json={"error": {"message": "Rate limited"}})
        )

        transport = SyncHTTPTransport(api_key="test-key", max_retries=0)
        with pytest.raises(PylonRateLimitError):
            transport.request("GET", "/test")
        transport.close()

    @respx.mock
    def test_validation_error(self):
        """Should raise PylonValidationError on 422."""
        respx.post("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(
                422, json={"error": {"message": "Validation failed"}}
            )
        )

        transport = SyncHTTPTransport(api_key="test-key")
        with pytest.raises(PylonValidationError):
            transport.request("POST", "/test", json={"invalid": "data"})
        transport.close()

    @respx.mock
    def test_server_error(self):
        """Should raise PylonServerError on 5xx."""
        respx.get("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(500, json={"error": {"message": "Server error"}})
        )

        transport = SyncHTTPTransport(api_key="test-key", max_retries=0)
        with pytest.raises(PylonServerError):
            transport.request("GET", "/test")
        transport.close()

    def test_context_manager(self):
        """Should work as context manager."""
        with SyncHTTPTransport(api_key="test-key") as transport:
            assert transport._client is not None


class TestAsyncHTTPTransport:
    """Tests for asynchronous HTTP transport."""

    def test_creates_with_defaults(self):
        """Should create transport with default settings."""
        transport = AsyncHTTPTransport(api_key="test-key")
        assert transport.base_url == "https://api.usepylon.com"
        assert transport.timeout == 30.0
        assert transport.max_retries == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_request(self):
        """Should make async GET requests."""
        respx.get("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(200, json={"data": "async_value"})
        )

        transport = AsyncHTTPTransport(api_key="test-key")
        response = await transport.arequest("GET", "/test")
        assert response == {"data": "async_value"}
        await transport.aclose()

    @pytest.mark.asyncio
    @respx.mock
    async def test_post_request(self):
        """Should make async POST requests with JSON body."""
        respx.post("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(201, json={"id": "async_new_123"})
        )

        transport = AsyncHTTPTransport(api_key="test-key")
        response = await transport.arequest("POST", "/test", json={"name": "test"})
        assert response == {"id": "async_new_123"}
        await transport.aclose()

    @pytest.mark.asyncio
    @respx.mock
    async def test_authentication_error(self):
        """Should raise PylonAuthenticationError on 401."""
        respx.get("https://api.usepylon.com/test").mock(
            return_value=httpx.Response(
                401, json={"error": {"message": "Unauthorized"}}
            )
        )

        transport = AsyncHTTPTransport(api_key="bad-key")
        with pytest.raises(PylonAuthenticationError):
            await transport.arequest("GET", "/test")
        await transport.aclose()

    @pytest.mark.asyncio
    @respx.mock
    async def test_not_found_error(self):
        """Should raise PylonNotFoundError on 404."""
        respx.get("https://api.usepylon.com/notfound").mock(
            return_value=httpx.Response(404, json={"error": {"message": "Not found"}})
        )

        transport = AsyncHTTPTransport(api_key="test-key")
        with pytest.raises(PylonNotFoundError):
            await transport.arequest("GET", "/notfound")
        await transport.aclose()

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Should work as async context manager."""
        async with AsyncHTTPTransport(api_key="test-key") as transport:
            assert transport._client is not None

