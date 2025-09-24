# Copyright 2025 Google
# Licensed under the Apache License, Version 2.0

import os, json
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import Client, types

MODEL_TEXT = "gemini-2.5-pro"          # coordinator/LLM if needed
MODEL_IMAGE = "imagen-3.0-generate-002" # Imagen (Vertex)

load_dotenv()

# Vertex-only for image gen
client = Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

def _coerce_style(style: dict) -> dict:
    """Tiny validator/normalizer for the style JSON."""
    brand = style.get("brand") or "Brand"
    palette = style.get("palette") or []
    vibe = style.get("vibe") or []
    fonts = style.get("fonts") or {}
    roles = style.get("roles") or {}
    # Ensure at least one color exists
    if not palette and roles.get("primary"):
        palette = [roles["primary"]]
    return {
        "brand": brand,
        "palette": palette[:6],
        "vibe": vibe[:6],
        "fonts": {
            "heading": (fonts.get("heading") or [])[:2],
            "body": (fonts.get("body") or [])[:2],
            "alt": (fonts.get("alt") or [])[:1],
        },
        "roles": {
            "primary": roles.get("primary", palette[0] if palette else "#111111"),
            "secondary": roles.get("secondary", palette[1] if len(palette) > 1 else "#666666"),
            "accent": roles.get("accent", palette[2] if len(palette) > 2 else "#999999"),
        },
    }

def _build_imagen_prompt(style: dict) -> str:
    """Turn the style JSON into a concise, deterministic Imagen prompt."""
    s = _coerce_style(style)
    brand = s["brand"]
    pal = ", ".join(s["palette"]) if s["palette"] else ""
    vibe = ", ".join(s["vibe"]) if s["vibe"] else "modern, clean"
    heading_fonts = ", ".join(s["fonts"]["heading"]) or "Inter"
    body_fonts = ", ".join(s["fonts"]["body"]) or "Inter"
    accent = s["roles"]["accent"]
    primary = s["roles"]["primary"]

    # Keep it simple and focused on vector/flat shapes for a logo comp
    return (
        f"Design a simple, original, flat vector logo for the brand '{brand}'. "
        f"Style: {vibe}. "
        f"Use a color direction inspired by this palette: {pal}. "
        f"Favor '{primary}' as the primary color and '{accent}' as an accent. "
        f"Typography inspiration (for wordmark feel): heading fonts {heading_fonts}; body fonts {body_fonts}. "
        "Constraints: minimal, geometric forms; strong silhouette; high contrast; no photo; no 3D; "
        "no copyrighted or trademarked elements; export on transparent or plain background."
    )

async def generate_logo_from_style(style_json: str, tool_context: "ToolContext"):
    """
    Tool: accepts JSON string describing style seed; generates a logo PNG and stores it as an artifact.
    Args:
      style_json: JSON string with keys like brand, palette, vibe, fonts, roles.
    Returns:
      {status, filename}
    """
    try:
        parsed = json.loads(style_json)
    except Exception as e:
        return {"status": "failed", "detail": f"Invalid JSON: {e}"}

    prompt = _build_imagen_prompt(parsed)

    # Call Imagen (Vertex)
    resp = client.models.generate_images(
        model=MODEL_IMAGE,
        prompt=prompt,
        config={"number_of_images": 1},
    )
    if not resp.generated_images:
        return {"status": "failed", "detail": "No image returned by Imagen."}

    png_bytes = resp.generated_images[0].image.image_bytes
    filename = f"logo_{(parsed.get('brand') or 'brand').lower().replace(' ','_')}.png"

    # Save to artifacts for download/reuse
    await tool_context.save_artifact(
        filename,
        types.Part.from_bytes(data=png_bytes, mime_type="image/png"),
    )

    return {
        "status": "success",
        "detail": "Logo generated and saved as artifact.",
        "filename": filename,
    }

logo_create_agent = Agent(
    model=MODEL_TEXT,
    name="logo_create_agent",
    description="Generates a logo PNG from a style JSON using Imagen, and stores it as an artifact.",
    instruction=(
        "The user provides a JSON style seed (brand, palette, fonts, roles, vibe). "
        "Call generate_logo_from_style(style_json=...) to create a logo image. "
        "If needed, call load_artifacts to list previously generated files. "
        "Return a short status JSON with the artifact filename."
    ),
    tools=[generate_logo_from_style, load_artifacts],
    output_key="logo_output",
)
