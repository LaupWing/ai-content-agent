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
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("Missing NOTION_API_KEY or NOTION_IDEAS_DATABASE_ID environment variables")

    # Ensure limit is within bounds
    limit = min(max(1, limit), 100)

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

    # Fetch ALL ideas (up to limit) without filtering - we'll filter client-side
    payload = {
        "page_size": limit
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

        # Parse and filter results client-side with keyword matching
        matching_ideas = []
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

            # Combine all searchable text (lowercase for case-insensitive search)
            searchable_text = f"{title} {description} {raw_text} {' '.join(tags)}".lower()

            # Check if ANY keyword matches (flexible matching)
            keyword_matches = sum(1 for keyword in keywords if keyword in searchable_text)

            # Include idea if at least one keyword matches
            if keyword_matches > 0:
                matching_ideas.append({
                    "page_id": page.get("id", ""),
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "raw_text": raw_text,
                    "match_score": keyword_matches  # How many keywords matched
                })

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
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("Missing NOTION_API_KEY or NOTION_IDEAS_DATABASE_ID environment variables")

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

    payload = {
        "properties": properties
    }

    try:
        response = requests.patch(
            f"{NOTION_BASE_URL}/pages/{page_id}",
            headers=HEADERS,
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        result = response.json()

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
