import os
import urllib.parse
from dotenv import load_dotenv
from groq import Groq
from supabase import create_client, Client
from playwright.sync_api import sync_playwright

load_dotenv()

# Initialize API Clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_KEY")
)

goal = input("\nWhat is your agent's goal today? ")

# 1. AI Generates Search Strategy using gpt-oss-20b
print("\n🤖 AI is creating search strategy...")
response = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": "Convert the user's goal into a concise search query. Return ONLY the search query."},
        {"role": "user", "content": goal}
    ]
)
search_query = response.choices[0].message.content.strip()
print(f"🎯 Search Query: {search_query}")

# Encode search query for URL
encoded_query = urllib.parse.quote_plus(search_query)
search_url = f"https://duckduckgo.com/?q={encoded_query}"

# 2. Direct Browser Action (No element typing required!)
print("\n🌐 Opening browser and fetching search results...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Go directly to search results page
    page.goto(search_url, wait_until="networkidle")
    page.wait_for_timeout(3000)
    
    # Grab page text
    page_text = page.locator("body").inner_text()
    browser.close()

# 3. AI Summarises Findings using gpt-oss-20b
print("\n🧠 Summarising findings...")
summary_response = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": "Summarize the key takeaways from this search result text in 3 concise bullet points."},
        {"role": "user", "content": page_text[:8000]}
    ]
)
final_summary = summary_response.choices[0].message.content.strip()

print("\n====================")
print("AGENT SUMMARY")
print("====================\n")
print(final_summary)

# 4. Save to Supabase Cloud Memory
print("\n☁️ Saving to Supabase Cloud Memory...")
try:
    data = supabase.table("agent_memories").insert({
        "user_goal": goal,
        "website_summary": final_summary
    }).execute()
    print("✅ Successfully saved memory to Supabase Cloud!")
except Exception as e:
    print(f"❌ Error saving to Supabase: {e}")