from typing import Dict, Any, List
import requests
import sys
import os

# Add parent directory to path to import notion_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from notion_client import get_database_schema


def get_existing_tags() -> Dict[str, Any]:
    """
    Fetch all existing tags from the Notion database.

    Returns:
        Dictionary containing list of existing tag names
    """
    try:
        # Retrieve the database schema
        database = get_database_schema()

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
