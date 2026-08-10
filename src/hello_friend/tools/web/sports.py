"""
Sports scores tool.

Returns structured football/soccer scores instead of search-result links.
Uses ESPN's public scoreboard endpoint.
"""

import logging
from datetime import datetime, timezone

import httpx
from langchain.tools import tool

logger = logging.getLogger(__name__)

ESPN_SCOREBOARD_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/"
    "soccer/eng.1/scoreboard"
)

TIMEOUT = 10.0


@tool
def search_sports(query: str) -> str:
    """
    Get current football/soccer scores and fixtures.

    Use this for requests about football scores, matches,
    fixtures, results, and games.

    The query can contain a team name or general request such as
    'today football scores'.
    """

    query = query.strip()

    if not query:
        return "Error: sports query is required."

    try:
        response = httpx.get(
            ESPN_SCOREBOARD_URL,
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        events = data.get("events", [])

        if not events:
            return (
                f"No football matches were found for today's "
                f"available schedule.\n"
                f"Query: {query}"
            )

        results: list[str] = []

        for event in events:
            competitions = event.get("competitions", [])

            if not competitions:
                continue

            competition = competitions[0]

            competitors = competition.get("competitors", [])

            if len(competitors) < 2:
                continue

            home = None
            away = None

            for team in competitors:
                if team.get("homeAway") == "home":
                    home = team
                elif team.get("homeAway") == "away":
                    away = team

            if not home or not away:
                continue

            home_name = home.get("team", {}).get(
                "displayName",
                "Unknown",
            )

            away_name = away.get("team", {}).get(
                "displayName",
                "Unknown",
            )

            home_score = home.get("score", "-")
            away_score = away.get("score", "-")

            status = (
                event.get("status", {})
                .get("type", {})
                .get("shortDetail", "Unknown")
            )

            results.append(
                f"{away_name} {away_score} - "
                f"{home_score} {home_name}\n"
                f"Status: {status}"
            )

        if not results:
            return "No readable football scores were found."

        return (
            "Today's football scores:\n\n"
            + "\n\n".join(results)
        )

    except httpx.TimeoutException:
        return "Error: sports request timed out."

    except httpx.HTTPError as exc:
        logger.exception("Sports request failed")
        return f"Error: could not retrieve football scores: {exc}"

    except (KeyError, IndexError, ValueError) as exc:
        logger.exception("Invalid sports response")
        return f"Error: could not understand sports data: {exc}"

    except Exception as exc:
        logger.exception("Unexpected sports error")
        return f"Error: could not retrieve football scores: {exc}"