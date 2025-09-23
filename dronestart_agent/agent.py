from google.adk.agents import Agent
from google.cloud import storage

def get_txt_file(path: str, bucket_name: str) -> str:
    """
    Reads a .txt file from Firebase Storage (Google Cloud Storage).

    Returns:
        The text content of the file as a string.
    """
    client = storage.Client()  # uses Application Default Credentials (ADC)
    bucket = client.bucket("dronestart-production.appspot.com")
    blob = bucket.blob("handboeken/NG56Njq7iTWBUAqsxkIipa3J8R32/S2ySsDZHfcMP32IceFBh/6_2.txt")

    if not blob.exists():
        raise FileNotFoundError(f"File {path}.txt not found in bucket {bucket_name}")

    return blob.download_as_text()



root_agent = Agent(
    name="dronestart_agent",
    model="gemini-2.0-flash",
    description="",
    instruction=(
    ),
)


# agents/root_agent.py
import os
from google.adk.tools import VertexAiSearchTool

# Point this to your Vertex AI Search data store that indexes ONE fixed doc (or folder)
# Example: projects/<PROJECT_ID>/locations/<REGION>/collections/default_collection/dataStores/<DATASTORE_ID>
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
