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
    ),
    tools=[],
)
