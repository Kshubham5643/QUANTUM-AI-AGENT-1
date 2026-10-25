from groq import Groq
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# User command
user_command = input("What do you want me to do? ")

# Ask AI what action to take
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": """
You are a browser assistant.

You can return only:

YOUTUBE: search query

or

GOOGLE: search query

Examples:

User: Search YouTube for AI news
Output: YOUTUBE: AI news

User: Search Google for Python tutorials
Output: GOOGLE: Python tutorials

Return only the action.
"""
        },
        {
            "role": "user",
            "content": user_command
        }
    ]
)

action = response.choices[0].message.content.strip()

print("\nAI Decision:")
print(action)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    # YouTube action
    if action.startswith("YOUTUBE:"):

        query = action.replace(
            "YOUTUBE:",
            ""
        ).strip()

        page.goto("https://youtube.com")

        page.locator(
            "input[name='search_query']"
        ).fill(query)

        page.keyboard.press("Enter")

        page.wait_for_timeout(3000)

        page.locator(
            "ytd-video-renderer"
        ).first.click()

    # Google action
    elif action.startswith("GOOGLE:"):

        query = action.replace(
            "GOOGLE:",
            ""
        ).strip()

        page.goto("https://google.com")

        page.locator(
            "textarea[name='q']"
        ).fill(query)

        page.keyboard.press("Enter")

    else:
        print("Unknown action")

    page.wait_for_timeout(10000)

    browser.close()