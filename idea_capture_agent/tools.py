from typing import Dict, Any, List, Optional
import os
import requests

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_IDEAS_DATABASE_ID", "")
NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION
}


def list_ideas(
    limit: int = 10,
    filter_by_tag: Optional[str] = None
) -> Dict[str, Any]:
    """
    List ideas from the Notion database.

    Args:
        limit: Maximum number of ideas to retrieve (default: 10, max: 100)
        filter_by_tag: Optional tag to filter ideas by (e.g., "feature-request")

    Returns:
        Dictionary with list of ideas containing title, description, tags, and page_id
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("Missing NOTION_API_KEY or NOTION_IDEAS_DATABASE_ID environment variables")

    # Ensure limit is within bounds
    limit = min(max(1, limit), 100)

    # Build the query payload
    payload = {
        "page_size": limit
    }

    # Add filter if tag is specified
    if filter_by_tag:
        payload["filter"] = {
            "property": "Tags",
            "multi_select": {
                "contains": filter_by_tag
            }
        }

    try:
        response = requests.post(
            f"{NOTION_BASE_URL}/databases/{NOTION_DATABASE_ID}/query",
            headers=HEADERS,
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        result = response.json()

        # Parse and format the results
        ideas = []
        for page in result.get("results", []):
            properties = page.get("properties", {})

            # Extract title
            title_property = properties.get("Title", {}).get("title", [])
            title = title_property[0].get("text", {}).get("content", "") if title_property else "Untitled"

            # Extract description
            desc_property = properties.get("Description", {}).get("rich_text", [])
            description = desc_property[0].get("text", {}).get("content", "") if desc_property else ""

            # Extract tags
            tags_property = properties.get("Tags", {}).get("multi_select", [])
            tags = [tag.get("name", "") for tag in tags_property]

            # Extract raw text
            raw_property = properties.get("Raw Text", {}).get("rich_text", [])
            raw_text = raw_property[0].get("text", {}).get("content", "") if raw_property else ""

            ideas.append({
                "page_id": page.get("id", ""),
                "title": title,
                "description": description,
                "tags": tags,
                "raw_text": raw_text
            })

        filter_msg = f" with tag '{filter_by_tag}'" if filter_by_tag else ""
        return {
            "success": True,
            "count": len(ideas),
            "ideas": ideas,
            "message": f"Retrieved {len(ideas)} idea(s){filter_msg}"
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "count": 0,
            "ideas": [],
            "error": str(e),
            "message": f"Failed to list ideas: {str(e)}"
        }
