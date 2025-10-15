from typing import Dict, Any, List
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


def create_idea_in_notion(
    title: str,
    description: str,
    raw_text: str,
    tags: List[str]
) -> Dict[str, Any]:
    """
    Create a new idea in Notion database.

    Args:
        title: Generated title for the idea (3-8 words)
        description: Cleaned up and structured description
        raw_text: Original raw text from the user (EXACT, unchanged)
        tags: List of 2-5 relevant tags

    Returns:
        Dictionary with page_id and confirmation message
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("Missing NOTION_API_KEY or NOTION_IDEAS_DATABASE_ID environment variables")

    properties = {
        "Title": {
            "title": [{"text": {"content": title}}]
        },
        "Description": {
            "rich_text": [{"text": {"content": description}}]
        },
        "Raw Text": {
            "rich_text": [{"text": {"content": raw_text}}]
        },
        "Tags": {
            "multi_select": [{"name": tag} for tag in tags]
        }
    }

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties
    }

    try:
        response = requests.post(
            f"{NOTION_BASE_URL}/pages",
            headers=HEADERS,
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        result = response.json()

        return {
            "success": True,
            "page_id": result["id"],
            "title": title,
            "tags": tags,
            "message": f"Idea '{title}' saved with tags: {', '.join(tags)}"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to save idea: {str(e)}"
        }
