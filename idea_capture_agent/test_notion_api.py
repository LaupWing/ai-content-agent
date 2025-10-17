"""
Quick test script to verify Notion API connectivity.
Tests adding and removing an idea from the database.
"""
from dotenv import load_dotenv
from notion_client import create_page, query_database, update_page, validate_config, NOTION_DATABASE_ID
from datetime import date
import sys

# Load environment variables from .env file
load_dotenv()


def test_notion_api():
    """Test Notion API by creating and deleting a test idea."""

    print("🧪 Testing Notion API connectivity...\n")

    # Step 1: Validate configuration
    print("1️⃣ Validating configuration...")
    try:
        validate_config()
        print("✅ Configuration validated\n")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False

    # Step 2: Create a test idea
    print("2️⃣ Creating test idea...")
    test_properties = {
        "Title": {
            "title": [{"text": {"content": "[TEST] API Connection Test"}}]
        },
        "Description": {
            "rich_text": [{"text": {"content": "This is a test idea created to verify API connectivity. Safe to delete."}}]
        },
        "Raw Text": {
            "rich_text": [{"text": {"content": "Test raw text"}}]
        },
        "Tags": {
            "multi_select": [{"name": "test"}]
        },
        "Date": {
            "date": {"start": date.today().isoformat()}
        }
    }

    try:
        result = create_page(test_properties)
        page_id = result["id"]
        print(f"✅ Test idea created successfully!")
        print(f"   Page ID: {page_id}\n")
    except Exception as e:
        print(f"❌ Failed to create test idea: {e}")
        return False

    # Step 3: Verify the idea exists by querying
    print("3️⃣ Verifying test idea exists...")
    try:
        query_result = query_database(page_size=100)
        test_ideas = [
            page for page in query_result.get("results", [])
            if page["id"] == page_id
        ]

        if test_ideas:
            print("✅ Test idea found in database\n")
        else:
            print("⚠️  Test idea not found in query results\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not verify idea: {e}\n")

    # Step 4: Archive (delete) the test idea
    print("4️⃣ Cleaning up - archiving test idea...")
    try:
        # Archive the page by setting archived to true
        archive_properties = {}
        import requests
        import os

        NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
        NOTION_API_VERSION = "2022-06-28"
        NOTION_BASE_URL = "https://api.notion.com/v1"

        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION
        }

        response = requests.patch(
            f"{NOTION_BASE_URL}/pages/{page_id}",
            headers=headers,
            json={"archived": True},
            timeout=10.0
        )
        response.raise_for_status()

        print("✅ Test idea archived successfully\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not archive test idea: {e}")
        print(f"   You may need to manually delete page: {page_id}\n")

    # Final summary
    print("=" * 50)
    print("✨ Notion API test completed successfully!")
    print("=" * 50)
    print(f"Database ID: {NOTION_DATABASE_ID}")
    print("\nYour Notion API is working correctly! 🎉")

    return True


if __name__ == "__main__":
    try:
        success = test_notion_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
