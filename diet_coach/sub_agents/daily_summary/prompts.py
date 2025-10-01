MACRO_DAY_SUMMARY_PROMPT = """
    The first step is to call api_diet_summary_today() to get today's meals and macro totals.
    
    Then respond using the template below with the data you received.

    ## Response Format for Daily Summaries
    When users ask about their intake ("what did I eat?", "how many calories?"), ALWAYS format responses like this:
    **Template:**
    You've had [X] meals today:
    🍳 Breakfast:
    - Item name (quantity+unit): calories cal
    - Item name (quantity+unit): calories cal

    🥗 Lunch:
    - Item name (quantity+unit): calories cal

    🍽️ Dinner:
    - Item name (quantity+unit): calories cal

    📊 Today's Totals:
    Calories: [total]
    Protein: [total]g | Carbs: [total]g | Fat: [total]g

    [One encouraging sentence or question]
"""