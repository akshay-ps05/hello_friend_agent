"""
Fetch a webpage and return its raw response content.
"""

import logging

import httpx
from langchain.tools import tool

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 12.0
MAX_FETCH_CHARS = 12_000
USER_AGENT = "Mozilla/5.0 (compatible; HelloFriend/3.0)"


def _validate_url(url: str) -> str:
    url = url.strip()

    if not url:
        raise ValueError("URL is required.")

    if not url.startswith(("http://", "https://")):
        raise ValueError(
            "Only absolute http:// or https:// URLs are supported."
        )

    return url


@tool
def fetch_webpage(url: str) -> str:
    """
    Fetch a webpage and return its URL, HTTP status, content type,
    and raw page text.

    Use this when you already have a specific URL and need the
    source content.
    """
    try:
        url = _validate_url(url)

        response = httpx.get(
            url,
            follow_redirects=True,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )

        response.raise_for_status()

        body = response.text[:MAX_FETCH_CHARS]

        if len(response.text) > MAX_FETCH_CHARS:
            body += "\n\n[content truncated]"

        return (
            f"URL: {response.url}\n"
            f"Status: {response.status_code}\n"
            f"Content-Type: "
            f"{response.headers.get('content-type', 'unknown')}\n\n"
            f"{body}"
        )

    except ValueError as exc:
        return f"Error: {exc}"

    except httpx.TimeoutException:
        return "Error: webpage request timed out."

    except httpx.HTTPStatusError as exc:
        logger.exception("Webpage returned HTTP error")
        return (
            f"Error: webpage returned HTTP "
            f"{exc.response.status_code}."
        )

    except httpx.HTTPError as exc:
        logger.exception("Webpage request failed")
        return f"Error: could not fetch webpage: {exc}"

    except Exception as exc:
        logger.exception("Unexpected webpage fetch error")
        return f"Error: could not fetch webpage: {exc}"