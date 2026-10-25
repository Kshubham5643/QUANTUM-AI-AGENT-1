from groq import Groq
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto("https://news.ycombinator.com")

    page.wait_for_timeout(3000)

    text = page.locator("body").inner_text()

    browser.close()

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "Summarize the most interesting tech news on this page."
        },
        {
            "role": "user",
            "content": text[:4000]
        }
    ]
)

print("\nAI SUMMARY:\n")

print(response.choices[0].message.content)