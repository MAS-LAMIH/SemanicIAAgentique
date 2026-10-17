"""Neutral loopback HTTP transport; no contract, capability or registry logic."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener
from .model import ApiResult


class HTTPTransport:
    def __init__(self, base_url: str):
        address = urlsplit(base_url)
        if (address.scheme != 'http' or address.hostname != '127.0.0.1' or
            not address.port or address.path or address.query or address.fragment or address.username):
            raise ValueError('Milestone 1 supports only a controlled 127.0.0.1 HTTP origin')
        self._base = base_url
        # Loopback requests need no external proxy. Redirects are not followed.
        from urllib.request import HTTPRedirectHandler
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        self._http = build_opener(ProxyHandler({}), NoRedirect())

    def _http_request(self, method: str, path: str, values=None) -> ApiResult:
        data = None if values is None else json.dumps(values).encode()
        request = Request(self._base + path, data=data, method=method,
                          headers={'Content-Type': 'application/json'})
        try:
            with self._http.open(request, timeout=5) as response:
                body = json.loads(response.read(1000000))
                if not isinstance(body, dict):
                    raise ValueError('Expected JSON object')
                return ApiResult(response.status, body)
        except HTTPError as error:
            try:
                body = json.loads(error.read(1000000))
            except (ValueError, OSError):
                body = {}
            return ApiResult(error.code, body if isinstance(body, dict) else {}, f'HTTP {error.code}')
        except (URLError, TimeoutError, OSError, ValueError) as error:
            return ApiResult(None, {}, f'{type(error).__name__}: {error}')

