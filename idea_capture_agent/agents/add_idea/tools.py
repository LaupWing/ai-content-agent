from typing import Dict, Any, List
import requests
from datetime import date
import sys
import os

# Add parent directory to path to import notion_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from notion_client import create_page


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
    # Get today's date in ISO format (YYYY-MM-DD)
    today = date.today().isoformat()

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
        },
        "Date": {
            "date": {"start": today}
        }
    }

    try:
        result = create_page(properties)

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
