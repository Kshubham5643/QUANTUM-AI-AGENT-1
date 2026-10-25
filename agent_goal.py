goal = input("Goal: ")

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": """
Convert the user's goal into a Google search query.

Return ONLY the search query.
"""
        },
        {
            "role": "user",
            "content": goal
        }
    ]
)

search_query = response.choices[0].message.content.strip()