# agent.py
# pip install google-adk python-dotenv google-genai
# Env:
#   GOOGLE_CLOUD_PROJECT=<your-project-id>
#   GOOGLE_CLOUD_LOCATION=us-central1   # (or your Vertex region)

import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import Client, types
import requests

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

load_dotenv()

MODEL_TEXT  = "gemini-2.5-pro"             # coordinator (can be any Gemini text model)
MODEL_IMAGE = "imagen-3.0-generate-002"    # Imagen text-to-image on Vertex

# Imagen client via Vertex AI
client = Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

# ------- one tiny tool: generate from plain text brief -------
async def generate_logo_from_text(brief: str, tool_context: "ToolContext"):
    """
    Takes a freeform text brief (palette, roles, vibe, fonts, notes),
    composes a concise image prompt, generates a PNG, and stores it as an artifact.
    """
    if not brief or not brief.strip():
        return {"status": "failed", "detail": "Empty brief"}

    # Keep it simple: inject the user's brief and add minimal constraints for logo comps
    prompt = (
        "Design a simple, original, flat vector LOGO.\n"
        "Use only shapes, no photos, no 3D, high contrast, strong silhouette.\n"
        "Inspiration and constraints (verbatim user brief below):\n\n"
        f"{brief.strip()}\n\n"
        "Output: a single centered logo on a clean background suitable for preview."
    )

    resp = client.models.generate_images(
        model=MODEL_IMAGE,
        prompt=prompt,
        config={"number_of_images": 1},
    )
    if not resp.generated_images:
        return {"status": "failed", "detail": "Imagen returned no image."}

    png_bytes = resp.generated_images[0].image.image_bytes
    filename = "logo.png"
    await tool_context.save_artifact(
        filename,
        types.Part.from_bytes(data=png_bytes, mime_type="image/png"),
    )
    return {"status": "success", "filename": filename}

async def generate_logo_dalle(prompt: str, tool_context: ToolContext):
    url = "https://api.openai.com/v1/images/generations"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {"model": "gpt-image-1", "prompt": prompt, "size": "512x512"}

    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    img_url = resp.json()["data"][0]["url"]

    # fetch the image bytes
    img_bytes = requests.get(img_url).content
    filename = "logo_dalle.png"

    await tool_context.save_artifact(
        filename,
        types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
    )
    return {"status": "success", "filename": filename}

# ------- the agent -------
logo_from_text_agent = Agent(
    model=MODEL_TEXT,
    name="logo_from_text_agent",
    description="Generates a logo image from a freeform brand/style brief.",
    instruction="""
You are a coordinator. The user will paste a short text brief describing colors, roles, vibe, fonts, and notes.
Call the tool `generate_logo_dalle(brief=<entire user message>)` to create one logo image.
After the tool finishes, return a tiny JSON like:
{"status":"success","artifact":"logo.png"}

Rules:
- Do not include base64 image data in text; rely on artifacts for the PNG.
- If the user asks where the file is, tell them it's available in artifacts as 'logo.png'.
""",
    tools=[generate_logo_dalle, load_artifacts],
)

# If you prefer this as your root agent:
root_agent = logo_from_text_agent
