from groq import Groq
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("")
)

user_input = input("What should I search on YouTube? ")

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "Return only a YouTube search query."
        },
        {
            "role": "user",
            "content": user_input
        }
    ]
)

query = response.choices[0].message.content.strip()

print("Searching:", query)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto("https://www.youtube.com")

    page.locator("input[name='search_query']").fill(query)

    page.keyboard.press("Enter")

    page.wait_for_timeout(10000)

    browser.close()