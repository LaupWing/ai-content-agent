from typing import Dict, Any
import sys
import os

# Add parent directory to path to import notion_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from notion_client import get_page, update_page


def append_discussion_to_idea(
    page_id: str,
    discussion_content: str
) -> Dict[str, Any]:
    """
    Append discussion/expansion content to an existing idea's description.

    Args:
        page_id: Notion page ID of the idea
        discussion_content: New discussion content to append

    Returns:
        Dictionary with success status and message
    """
    try:
        # Get current page
        page = get_page(page_id)

        # Extract current description
        properties = page.get("properties", {})
        desc_property = properties.get("Description", {}).get("rich_text", [])
        current_description = desc_property[0].get("text", {}).get("content", "") if desc_property else ""

        # Append discussion with clear separator
        separator = "\n\n---\n\n## Discussion & Expansion\n\n" if current_description else "## Discussion & Expansion\n\n"
        new_description = f"{current_description}{separator}{discussion_content}"

        # Update the page
        update_properties = {
            "Description": {
                "rich_text": [{"text": {"content": new_description}}]
            }
        }

        update_page(page_id, update_properties)

        return {
            "success": True,
            "page_id": page_id,
            "message": "Discussion appended to idea successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to append discussion: {str(e)}"
        }
