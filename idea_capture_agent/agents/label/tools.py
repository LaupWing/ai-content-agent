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


def get_existing_tags() -> Dict[str, Any]:
    """
    Fetch all existing tags from the Notion database.

    Returns:
        Dictionary containing list of existing tag names
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("Missing NOTION_API_KEY or NOTION_IDEAS_DATABASE_ID environment variables")

    try:
        # Retrieve the database to get its properties schema
        response = requests.get(
            f"{NOTION_BASE_URL}/databases/{NOTION_DATABASE_ID}",
            headers=HEADERS,
            timeout=10.0
        )
        response.raise_for_status()
        database = response.json()

        # Extract existing tags from the Tags multi-select property
        tags_property = database.get("properties", {}).get("Tags", {})

        if tags_property.get("type") == "multi_select":
            existing_tags = [
                option["name"]
                for option in tags_property.get("multi_select", {}).get("options", [])
            ]

            return {
                "success": True,
                "tags": existing_tags,
                "count": len(existing_tags),
                "message": f"Found {len(existing_tags)} existing tags"
            }
        else:
            return {
                "success": False,
                "tags": [],
                "message": "Tags property not found or not a multi-select"
            }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "tags": [],
            "error": str(e),
            "message": f"Failed to fetch tags: {str(e)}"
        }
