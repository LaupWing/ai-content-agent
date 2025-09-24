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
        "You must first query the vertex_ai_search tool for every user question and base your answer "
        "only on the retrieved passages from the indexed document. "
        "If no relevant passage is found, say you couldn't find it in the document. "
        "Be concise and include brief citations (section/heading/line) when available. "
        "Do not rely on prior knowledge; do not fabricate content."
    ),
    tools=[vertex_search_tool],
)
