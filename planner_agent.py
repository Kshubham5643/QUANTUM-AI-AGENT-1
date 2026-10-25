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

goal = input("\nEnter a complex goal for your Agent: ")

# 1. AI Generates Multi-Step Execution Plan using gpt-oss-20b
print("\n🤖 AI is analyzing goal and generating multi-step plan...")
plan_response = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system", 
            "content": "You are an autonomous AI planner. Break the user's goal down into exactly 2 or 3 clear, sequential search tasks. Format each task as a short line starting with 'Step X: '"
        },
        {"role": "user", "content": goal}
    ]
)

plan_text = plan_response.choices[0].message.content.strip()

print("\n====================")
print("AGENT EXECUTION PLAN")
print("====================\n")
print(plan_text)

# Extract steps from the plan
steps = [line.strip() for line in plan_text.split("\n") if line.strip().startswith("Step")]

if not steps:
    steps = [f"Step 1: Research {goal}"]

all_summaries = []

# 2. Execute Each Step Autonomously
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    
    for idx, step in enumerate(steps, 1):
        print(f"\n🚀 Executing {step}...")
        
        # Formulate search query for this specific step
        query_response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "Convert this step into a concise 3-4 word DuckDuckGo search query. Return ONLY the search query."},
                {"role": "user", "content": step}
            ]
        )
        search_query = query_response.choices[0].message.content.strip()
        encoded_query = urllib.parse.quote_plus(search_query)
        search_url = f"https://duckduckgo.com/?q={encoded_query}"
        
        # Navigate browser
        page = browser.new_page()
        page.goto(search_url, wait_until="networkidle")
        page.wait_for_timeout(2500)
        
        # Scrape text
        page_text = page.locator("body").inner_text()
        page.close()
        
        # Summarize step findings
        step_summary_resp = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "Summarize key findings for this step in 2 bullet points."},
                {"role": "user", "content": page_text[:6000]}
            ]
        )
        step_summary = step_summary_resp.choices[0].message.content.strip()
        all_summaries.append(f"### {step}\n{step_summary}")
        print(f"✅ Finished {step}!")

    browser.close()

# 3. Consolidate Final Findings
combined_findings = "\n\n".join(all_summaries)

print("\n====================")
print("FINAL CONSOLIDATED REPORT")
print("====================\n")
print(combined_findings)

# 4. Save Multi-Step Execution to Supabase Cloud
print("\n☁️ Persisting complete multi-step report to Supabase...")
try:
    supabase.table("agent_memories").insert({
        "user_goal": goal,
        "website_summary": combined_findings
    }).execute()
    print("✅ Successfully saved multi-step plan memory to Supabase Cloud!")
except Exception as e:
    print(f"❌ Error saving to Supabase: {e}")