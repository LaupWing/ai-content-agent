from google.adk.agents import Agent

root_agent = Agent(
    name="styleboard_creator",
    model="gemini-1.5-flash",  # multimodal; reads the uploaded image
    description="Creates a style seed from an attached image (palette, roles, vibe, fonts).",
    instruction=(
        "You are a brand stylist. The user will ATTACH one image in this chat.\n"
        "Analyze the attached image and OUTPUT STRICT JSON ONLY with this shape:\n"
        "{\n"
        '  "palette": ["#RRGGBB", "..."],                // up to 6, most important first\n'
        '  "roles": { "primary": "#...", "secondary": "#...", "accent": "#..." },\n'
        '  "vibe": ["adjective1","adjective2","adjective3"],\n'
        '  "fonts": { "heading": ["Google Font A","Google Font B"],\n'
        '             "body": ["Google Font C","Google Font D"],\n'
        '             "alt": ["Display Font"] },\n'
        '  "notes": ["short suggestion 1","short suggestion 2"],\n'
        '  "css_vars": { "--color-primary": "#...", "--color-secondary":"#...", "--color-accent":"#..." }\n'
        "}\n"
        "Rules:\n"
        "- Use colors actually present in the image (hex).\n"
        "- Pick roles from the palette.\n"
        "- Use only Google Fonts in suggestions.\n"
        "- NO extra text, explanations, or markdown — return JSON only.\n"
        "- If no image is attached, return: {\"status\":\"error\",\"error\":\"no_image\"}\n"
    ),
    tools=[],  
)
