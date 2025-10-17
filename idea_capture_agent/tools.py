from typing import Dict, Any, List, Optional
import requests
from notion_client import query_database, get_page, update_page, parse_idea_from_page


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
    # Build filter if tag is specified
    filter_config = None
    if filter_by_tag:
        filter_config = {
            "property": "Tags",
            "multi_select": {
                "contains": filter_by_tag
            }
        }

    try:
        result = query_database(page_size=limit, filter_config=filter_config)

        # Parse and format the results
        ideas = [parse_idea_from_page(page) for page in result.get("results", [])]

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


def query_ideas(
    search_text: str,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Search for ideas in the Notion database by keywords.
    Extracts keywords from search_text and finds ideas matching any of them.
    Keywords can match in any order and search is case-insensitive.

    Args:
        search_text: Text to search for (e.g., "delete blog automation")
        limit: Maximum number of ideas to retrieve (default: 100, max: 100)

    Returns:
        Dictionary with list of matching ideas containing title, description, tags, and page_id
    """
    # Extract keywords - split by spaces and filter out common words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    keywords = [
        word.lower().strip()
        for word in search_text.split()
        if word.lower().strip() and word.lower().strip() not in stop_words
    ]

    # If no valid keywords, use the original search text
    if not keywords:
        keywords = [search_text.lower()]

    try:
        result = query_database(page_size=limit)

        # Parse and filter results client-side with keyword matching
        matching_ideas = []
        for page in result.get("results", []):
            idea = parse_idea_from_page(page)

            # Combine all searchable text (lowercase for case-insensitive search)
            searchable_text = f"{idea['title']} {idea['description']} {idea['raw_text']} {' '.join(idea['tags'])}".lower()

            # Check if ANY keyword matches (flexible matching)
            keyword_matches = sum(1 for keyword in keywords if keyword in searchable_text)

            # Include idea if at least one keyword matches
            if keyword_matches > 0:
                idea["match_score"] = keyword_matches
                matching_ideas.append(idea)

        # Sort by match score (most matching keywords first)
        matching_ideas.sort(key=lambda x: x["match_score"], reverse=True)

        # Remove match_score from final results
        for idea in matching_ideas:
            del idea["match_score"]

        return {
            "success": True,
            "count": len(matching_ideas),
            "ideas": matching_ideas,
            "keywords": keywords,
            "message": f"Found {len(matching_ideas)} idea(s) matching keywords: {', '.join(keywords)}"
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "count": 0,
            "ideas": [],
            "error": str(e),
            "message": f"Failed to query ideas: {str(e)}"
        }


def update_idea(
    page_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update an existing idea in the Notion database.

    Args:
        page_id: The Notion page ID of the idea to update
        title: New title (optional)
        description: New description (optional)
        tags: New list of tags (optional)

    Returns:
        Dictionary with success status and confirmation message
    """
    # Build properties object with only the fields to update
    properties = {}

    if title is not None:
        properties["Title"] = {
            "title": [{"text": {"content": title}}]
        }

    if description is not None:
        properties["Description"] = {
            "rich_text": [{"text": {"content": description}}]
        }

    if tags is not None:
        properties["Tags"] = {
            "multi_select": [{"name": tag} for tag in tags]
        }

    # If no fields to update, return error
    if not properties:
        return {
            "success": False,
            "message": "No fields provided to update"
        }

    try:
        result = update_page(page_id, properties)

        updated_fields = []
        if title is not None:
            updated_fields.append(f"title to '{title}'")
        if description is not None:
            updated_fields.append("description")
        if tags is not None:
            updated_fields.append(f"tags to {tags}")

        return {
            "success": True,
            "page_id": result["id"],
            "message": f"Updated {', '.join(updated_fields)}"
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update idea: {str(e)}"
        }


def expand_idea(
    page_id: str,
    expanded_content: str
) -> Dict[str, Any]:
    """
    Expand an existing idea by appending new content to its description.
    Useful for adding details, thoughts, or elaborations to an idea.

    Args:
        page_id: The Notion page ID of the idea to expand
        expanded_content: New content to append to the existing description

    Returns:
        Dictionary with success status and confirmation message
    """
    try:
        # First, fetch the current idea to get existing description
        page = get_page(page_id)

        # Extract current description
        properties = page.get("properties", {})
        desc_property = properties.get("Description", {}).get("rich_text", [])
        current_description = desc_property[0].get("text", {}).get("content", "") if desc_property else ""

        # Append new content with a separator
        separator = "\n\n---\n\n" if current_description else ""
        new_description = f"{current_description}{separator}{expanded_content}"

        # Update the page with expanded description
        properties = {
            "Description": {
                "rich_text": [{"text": {"content": new_description}}]
            }
        }

        update_page(page_id, properties)

        return {
            "success": True,
            "page_id": page_id,
            "message": f"Expanded idea with new content ({len(expanded_content)} characters added)"
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to expand idea: {str(e)}"
        }
