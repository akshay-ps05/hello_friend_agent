"""
Extract readable text from webpages.
"""

import logging
import re
from html import unescape
from html.parser import HTMLParser

import httpx
from langchain.tools import tool

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 12.0
MAX_EXTRACT_CHARS = 9_000
USER_AGENT = "Mozilla/5.0 (compatible; HelloFriend/3.0)"


class _ContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()

        self.title = ""
        self.text_parts: list[str] = []

        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag in {"script", "style", "noscript", "svg", "canvas"}:
            self._skip_depth += 1

        elif tag == "title":
            self._in_title = True

        elif tag in {
            "p",
            "br",
            "li",
            "h1",
            "h2",
            "h3",
            "article",
            "section",
        }:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
        } and self._skip_depth:
            self._skip_depth -= 1

        elif tag == "title":
            self._in_title = False

        elif tag in {"p", "li", "h1", "h2", "h3"}:
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return

        if self._in_title:
            self.title += data
            return

        self.text_parts.append(data)


def _clean_text(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


@tool
def extract_content(url: str) -> str:
    """
    Fetch a webpage and extract readable text from its HTML.

    Use this for research when you need the actual article,
    documentation, or page content rather than just search results.
    """
    url = url.strip()

    if not url:
        return "Error: URL is required."

    if not url.startswith(("http://", "https://")):
        return (
            "Error: only absolute http:// or https:// "
            "URLs are supported."
        )

    try:
        response = httpx.get(
            url,
            follow_redirects=True,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )

        response.raise_for_status()

        parser = _ContentParser()
        parser.feed(response.text)

        title = _clean_text(parser.title)
        content = _clean_text(" ".join(parser.text_parts))

        if len(content) > MAX_EXTRACT_CHARS:
            content = (
                f"{content[:MAX_EXTRACT_CHARS]}\n\n"
                "[content truncated]"
            )

        if not content:
            return "No readable text content found on that page."

        if title:
            return (
                f"Title: {title}\n"
                f"URL: {response.url}\n\n"
                f"{content}"
            )

        return f"URL: {response.url}\n\n{content}"

    except httpx.TimeoutException:
        return "Error: webpage extraction timed out."

    except httpx.HTTPStatusError as exc:
        logger.exception("Webpage extraction HTTP error")
        return (
            f"Error: webpage returned HTTP "
            f"{exc.response.status_code}."
        )

    except httpx.HTTPError as exc:
        logger.exception("Webpage extraction failed")
        return f"Error: could not extract webpage: {exc}"

    except Exception as exc:
        logger.exception("Unexpected webpage extraction error")
        return f"Error: could not extract webpage: {exc}"