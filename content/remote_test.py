# test_remote.py
import asyncio
from vertexai import agent_engines
from google.genai import types

RESOURCE = "projects/770732600651/locations/europe-west4/reasoningEngines/900755109846188032"

async def main():
    app = agent_engines.get(RESOURCE)

    # 1) Create a session (store session_id in your DB/UI)
    s = await app.async_create_session(user_id="u_123")
    sid = s["id"]
    print("sessionId:", sid)

    # 2) Ask for workouts (text only)
    print("\n-- Workouts --")
    async for ev in app.async_stream_query(
        user_id="u_123", session_id=sid, message="What workouts do I need to do today?"
    ):
        part = ev.get("content", {}).get("parts", [{}])[0]
        if "text" in part:
            print(part["text"], end="", flush=True)

    # 3) Analyze a meal image (GCS URI)
    print("\n\n-- Analyze Meal --")
    txt = types.Part.from_text("Estimate macros for this meal. Return STRICT JSON only.")
    img = types.Part.from_uri("gs://fitness_coach/meals/demo.jpg", "image/jpeg")
    async for ev in app.async_stream_query(
        user_id="u_123", session_id=sid, message=[txt, img]
    ):
        part = ev.get("content", {}).get("parts", [{}])[0]
        if "text" in part:
            print(part["text"], end="", flush=True)

asyncio.run(main())
