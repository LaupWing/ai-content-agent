from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
import os

DATASTORE_PATH = os.getenv("VERTEX_SEARCH_DATASTORE", "projects/CHANGE_ME/locations/REGION/collections/default_collection/dataStores/DATASTORE_ID")

vertex_search_tool = VertexAiSearchTool(data_store_id=DATASTORE_PATH)

root_agent = Agent(
    name="dronestart_doc_bot",
    model="gemini-2.0-flash",
    description="Answers questions about a single legal document indexed from Firebase Storage (GCS).",
    instruction=(
        "You must first query the vertex_ai_search tool for every user question and base your answer on the retrieved results. "
    ),
    tools=[vertex_search_tool],
)
