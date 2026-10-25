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

    titles = page.locator(".titleline a").all_inner_texts()

    print("\nHEADLINES:\n")

    for i, title in enumerate(titles[:10]):
        print(f"{i + 1}. {title}")

    prompt = "\n".join(
        [f"{i+1}. {title}" for i, title in enumerate(titles[:10])]
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": """
Choose the most interesting tech article.

Return ONLY the number.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    choice = response.choices[0].message.content.strip()

    print("\nAI CHOSE:", choice)

    try:
        article_number = int(choice)

        page.locator(".titleline a").nth(
            article_number - 1
        ).click()

        page.wait_for_timeout(10000)

    except:
        print("AI returned invalid choice")

    browser.close()