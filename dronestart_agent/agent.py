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
    blob = bucket.blob("handboeken/1fdG53b4RyP25wVOGkYCYUZjTam2/5BGNS1dqjXrTxoviRtya/1_1.txt")

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
