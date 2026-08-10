"""
Live web search tool.

Uses DuckDuckGo's HTML endpoint so no separate search API key is required.
"""

from __future__ import annotations

import json
import logging
import re
from html import unescape
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import httpx
from langchain.tools import tool

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 12.0
MAX_SEARCH_RESULTS = 5
USER_AGENT = "Mozilla/5.0 (compatible; HelloFriend/3.0)"


class _SearchParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []

        self._in_title = False
        self._in_snippet = False

        self._current_title: list[str] = []
        self._current_snippet: list[str] = []
        self._current_url = ""

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "") or ""

        if tag == "a" and "result__a" in classes:
            self._in_title = True
            self._current_title = []
            self._current_snippet = []
            self._current_url = _unwrap_duckduckgo_url(
                attrs_dict.get("href", "")
            )

        elif "result__snippet" in classes:
            self._in_snippet = True

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._current_title.append(data)

        elif self._in_snippet:
            self._current_snippet.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_title:
            self._in_title = False

            title = _clean_text(" ".join(self._current_title))

            if title and self._current_url:
                self.results.append(
                    {
                        "title": title,
                        "url": self._current_url,
                        "snippet": "",
                    }
                )

        elif self._in_snippet:
            self._in_snippet = False

            if self.results:
                self.results[-1]["snippet"] = _clean_text(
                    " ".join(self._current_snippet)
                )


def _clean_text(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _unwrap_duckduckgo_url(url: str) -> str:
    if not url:
        return ""

    parsed = urlparse(url)

    if parsed.path == "/l/":
        target = parse_qs(parsed.query).get("uddg")

        if target:
            return unquote(target[0])

    return url


def _search(query: str) -> str:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"

    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=DEFAULT_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )

    response.raise_for_status()

    parser = _SearchParser()
    parser.feed(response.text)

    results = parser.results[:MAX_SEARCH_RESULTS]

    if not results:
        return "No search results found."

    return json.dumps(
        results,
        ensure_ascii=False,
        indent=2,
    )


@tool
def web_search(query: str) -> str:
    """
    Search the live web for current or general information.

    Use this for research, documentation, recent information, facts,
    websites, or topics that may have changed.
    """
    query = query.strip()

    if not query:
        return "Error: search query is required."

    try:
        return _search(query)

    except httpx.TimeoutException:
        return "Error: web search timed out."

    except httpx.HTTPStatusError as exc:
        logger.exception("Web search HTTP error")
        return f"Error: web search failed with HTTP {exc.response.status_code}."

    except httpx.HTTPError as exc:
        logger.exception("Web search HTTP error")
        return f"Error: web search failed: {exc}"

    except Exception as exc:
        logger.exception("Unexpected web search error")
        return f"Error: web search failed: {exc}"