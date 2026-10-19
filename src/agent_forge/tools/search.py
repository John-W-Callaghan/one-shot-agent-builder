"""Web search tool placeholder.

In a production version, this would integrate with a search API
(Tavily, SerpAPI, etc.) to let agents research libraries and docs.
For the portfolio version, agents rely on their training knowledge.
"""


def search_docs(query: str) -> list[dict[str, str]]:
    """Search for documentation and best practices.

    Returns a list of {title, snippet, url} results.

    NOTE: This is a placeholder. To enable real search, add a search
    API key to .env and implement the API call here.
    """
    return [
        {
            "title": f"Search results for: {query}",
            "snippet": "Search not configured. Agents will use training knowledge.",
            "url": "",
        }
    ]
