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

    headlines = page.locator(".titleline a")

    titles = headlines.all_inner_texts()

    print("\nHEADLINES:\n")

    for i, title in enumerate(titles[:10]):
        print(f"{i+1}. {title}")

    headline_text = "\n".join(
        [f"{i+1}. {title}" for i, title in enumerate(titles[:10])]
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "Choose the most interesting AI or technology article. Return only the number."
            },
            {
                "role": "user",
                "content": headline_text
            }
        ]
    )

    choice = response.choices[0].message.content.strip()

    print(f"\nAI chose article: {choice}")

    article_index = int(choice) - 1

    headlines.nth(article_index).click()

    page.wait_for_timeout(5000)

    article_text = page.locator("body").inner_text()

    browser.close()

summary = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": """
Summarise this article.

Format:

Title:
Summary:
Key Points:
"""
        },
        {
            "role": "user",
            "content": article_text[:8000]
        }
    ]
)

print("\n====================")
print("ARTICLE SUMMARY")
print("====================\n")
print(summary.choices[0].message.content)