"""
Centralized Notion API client for idea management.
Provides reusable functions for interacting with the Notion API.
"""
from typing import Dict, Any, Optional
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Notion API Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_IDEAS_DATABASE_ID", "")
NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION
}


def validate_config() -> None:
    """
    Validate that required Notion configuration is present.

    Raises:
        ValueError: If NOTION_API_KEY or NOTION_DATABASE_ID is missing
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("Missing NOTION_API_KEY or NOTION_IDEAS_DATABASE_ID environment variables")


def parse_idea_from_page(page: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and parse idea properties from a Notion page object.

    Args:
        page: Raw Notion page object from API response

    Returns:
        Dictionary containing parsed idea fields:
        - page_id: Notion page ID
        - title: Idea title
        - description: Idea description
        - tags: List of tag names
        - raw_text: Raw text content
    """
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

    return {
        "page_id": page.get("id", ""),
        "title": title,
        "description": description,
        "tags": tags,
        "raw_text": raw_text
    }


def query_database(
    page_size: int = 100,
    filter_config: Optional[Dict[str, Any]] = None,
    timeout: float = 10.0
) -> Dict[str, Any]:
    """
    Query the Notion database with optional filters.

    Args:
        page_size: Number of results to return (1-100)
        filter_config: Optional Notion filter object
        timeout: Request timeout in seconds

    Returns:
        Raw JSON response from Notion API

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    validate_config()

    # Ensure page_size is within bounds
    page_size = min(max(1, page_size), 100)

    # Build payload
    payload = {"page_size": page_size}
    if filter_config:
        payload["filter"] = filter_config

    response = requests.post(
        f"{NOTION_BASE_URL}/databases/{NOTION_DATABASE_ID}/query",
        headers=HEADERS,
        json=payload,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()


def get_page(page_id: str, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Retrieve a single Notion page by ID.

    Args:
        page_id: Notion page ID
        timeout: Request timeout in seconds

    Returns:
        Raw JSON response from Notion API

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    validate_config()

    response = requests.get(
        f"{NOTION_BASE_URL}/pages/{page_id}",
        headers=HEADERS,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()


def update_page(
    page_id: str,
    properties: Dict[str, Any],
    timeout: float = 10.0
) -> Dict[str, Any]:
    """
    Update a Notion page's properties.

    Args:
        page_id: Notion page ID
        properties: Dictionary of properties to update
        timeout: Request timeout in seconds

    Returns:
        Raw JSON response from Notion API

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    validate_config()

    payload = {"properties": properties}

    response = requests.patch(
        f"{NOTION_BASE_URL}/pages/{page_id}",
        headers=HEADERS,
        json=payload,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()


def create_page(
    properties: Dict[str, Any],
    timeout: float = 10.0
) -> Dict[str, Any]:
    """
    Create a new page in the Notion database.

    Args:
        properties: Dictionary of properties for the new page
        timeout: Request timeout in seconds

    Returns:
        Raw JSON response from Notion API

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    validate_config()

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties
    }

    response = requests.post(
        f"{NOTION_BASE_URL}/pages",
        headers=HEADERS,
        json=payload,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()


def get_database_schema(timeout: float = 10.0) -> Dict[str, Any]:
    """
    Retrieve the database schema/metadata.

    Args:
        timeout: Request timeout in seconds

    Returns:
        Raw JSON response from Notion API containing database schema

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    validate_config()

    response = requests.get(
        f"{NOTION_BASE_URL}/databases/{NOTION_DATABASE_ID}",
        headers=HEADERS,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()
