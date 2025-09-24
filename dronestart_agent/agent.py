from google.adk.agents import Agent
import os
import mimetypes
from typing import Dict, Any
from google import genai
from google.genai import types

API_KEY   = os.getenv("GOOGLE_API_KEY")            # <-- required
MODEL     = os.getenv("FILES_MODEL", "gemini-2.0-flash")
LOCAL_DOC = os.getenv("LOCAL_DOC", "./1_9.txt")  # <-- set this

def files_qa(question: str) -> Dict[str, Any]:
    """
    Uploads LOCAL_DOC to Gemini Files API and asks the model the given question grounded on that file.
    Returns: {"answer": str, "file_uri": str, "mime_type": str}
    """
    if not API_KEY:
        raise ValueError("Set GOOGLE_API_KEY env var to your Gemini API key.")
    if not os.path.exists(LOCAL_DOC):
        raise ValueError(f"LOCAL_DOC not found: {LOCAL_DOC}")

    client = genai.Client(api_key=API_KEY)

    mime, _ = mimetypes.guess_type(LOCAL_DOC)
    mime = mime or "text/plain"

    uploaded = client.files.upload(file=LOCAL_DOC, mime_type=mime)

    resp = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(text=question),
                    types.Part(file_data=types.FileData(
                        file_uri=uploaded.uri,
                        mime_type=uploaded.mime_type,
                    )),
                ],
            )
        ],
    )

    return {
        "answer": resp.text or "",
        "file_uri": uploaded.uri,
        "mime_type": uploaded.mime_type,
    }

root_agent = Agent(
    name="files_api_doc_bot",
    model="gemini-2.0-flash",  # keep using the same model family
    description="Answers questions about a local document by uploading it to Gemini Files API.",
    instruction=(
        "For each user question, CALL the files_qa(question=<user message>) tool and "
        "return ONLY the tool's 'answer'. Do not answer from general knowledge."
    ),
    tools=[files_qa]
)
