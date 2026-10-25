from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto("https://news.ycombinator.com")

    page.wait_for_timeout(3000)

    print(page.title())

    print("\n----- PAGE TEXT -----\n")

    text = page.locator("body").inner_text()

    print(text[:3000])

    browser.close()