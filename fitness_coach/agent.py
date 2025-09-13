from google.adk.agents import Agent

macro_scanner_agent = Agent(
    name="macro_scanner_v1",
    model="gemini-2.0-flash",
    description="Vision-only macro estimator from a meal photo.",
    instruction=(
        "The user will include an image. RETURN ONLY STRICT JSON:\n"
        "{items:[{name,grams,protein_g,carb_g,fat_g,kcal}],"
        " totals:{protein_g,carb_g,fat_g,kcal}, confidence:number, notes:string}\n"
        "- Identify visible foods, estimate grams and macros using typical macro density.\n"
        "- If visibility is poor, explain in 'notes' and lower confidence.\n"
        "- Do not output any text outside JSON."
    )
)

swaps_agent = Agent(
    name="food_swaps",
    model="gemini-2.0-flash",
    description="Suggest practical food swaps with kcal deltas; can use prior macro JSON.",
    instruction=(
        "If macro JSON is provided, base deltas on it. Return a short bullet list with each swap's "
        "new kcal and Δkcal (negative is fewer), and a one-line summary."
    ),
)

root_agent = Agent(
    name="diet_agent",
    model="gemini-2.0-flash",
    description="Diet coach that can analyze meal photos OR recommend lower-calorie swaps.",
    instruction=(
        "Decide which specialist to use:\n"
        "- If the user includes an IMAGE or asks to analyze a meal, TRANSFER to 'macro_scanner'.\n"
        "- If the user asks for swaps/alternatives/less calories, TRANSFER to 'food_swaps'.\n"
        "When relevant, pass along the previous macro JSON in context/state."
    ),
    sub_agents=[macro_scanner_agent, swaps_agent],  # enables LLM-driven delegation
)