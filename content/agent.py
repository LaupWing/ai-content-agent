from google.adk.agents import Agent

root_agent = Agent(
    name="food_macro_vision_agent_v1",
    model="gemini-2.0-flash",
    description="Analyzes a meal photo and returns estimated macros.",
    instruction=(
        "You are a nutrition estimator. The user will send a photo of food. "
        "Do ALL of the following, and RETURN ONLY JSON:\n"
        "1) Identify distinct food items visible.\n"
        "2) Estimate portion grams per item (state assumptions: e.g., plate size, typical serving).\n"
        "3) Estimate macros per item (protein_g, carb_g, fat_g) and total calories (kcal).\n"
        "4) Provide overall totals and a confidence score (0–1).\n"
        "Rules:\n"
        "- If multiple foods are present, list each with grams and macros.\n"
        "- If visibility is poor, say so in 'notes' and lower confidence.\n"
        "- Use typical macro density for common foods when unsure; avoid hallucinating rare items.\n"
        "- Output strict JSON with keys: items[], totals{}, confidence, notes."
    ),
    tools=[]
)
