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

def search_memory(query: str) -> str:
    """Retrieves context from Supabase cloud memory."""
    try:
        response = supabase.table("agent_memories").select("user_goal, website_summary").order("created_at", desc=True).limit(5).execute()
        memories = response.data
        if not memories:
            return "No prior memories found."
        
        context = ""
        for m in memories:
            context += f"Goal: {m.get('user_goal')}\nSummary: {m.get('website_summary')}\n---\n"
        return context
    except Exception as e:
        return f"Error reading memory: {e}"

def execute_web_search(goal: str) -> str:
    """Plans and executes web search autonomously using Playwright."""
    print("\n🤖 AI is creating execution query...")
    query_resp = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "Convert the goal into a concise search query. Return ONLY the search query."},
            {"role": "user", "content": goal}
        ]
    )
    search_query = query_resp.choices[0].message.content.strip()
    encoded_query = urllib.parse.quote_plus(search_query)
    search_url = f"https://duckduckgo.com/?q={encoded_query}"
    
    print("\n🌐 Opening browser to fetch live data...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(search_url, wait_until="networkidle")
        page.wait_for_timeout(2500)
        page_text = page.locator("body").inner_text()
        browser.close()

    print("\n🧠 Summarising web results...")
    summary_resp = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "Summarize key findings in 3 bullet points."},
            {"role": "user", "content": page_text[:7000]}
        ]
    )
    summary = summary_resp.choices[0].message.content.strip()

    # Save to Supabase
    try:
        supabase.table("agent_memories").insert({
            "user_goal": goal,
            "website_summary": summary
        }).execute()
        print("✅ Saved new research to Supabase Cloud!")
    except Exception as e:
        print(f"❌ Error persisting to Supabase: {e}")

    return summary

def main():
    print("==================================================")
    print("🤖 AUTONOMOUS AI AGENT CONSOLE (type 'exit' to quit)")
    print("==================================================")

    while True:
        user_input = input("\nUser > ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break

        if not user_input:
            continue

        # Decide action: Memory, Research, or Direct Answer
        decision_resp = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system", 
                    "content": "Classify user prompt into one category: 'SEARCH_WEB' (needs real-time web info), 'MEMORY' (asking about past stored tasks/notes), or 'DIRECT' (general answer). Return ONLY the category tag."
                },
                {"role": "user", "content": user_input}
            ]
        )
        intent = decision_resp.choices[0].message.content.strip()

        if "SEARCH_WEB" in intent:
            result = execute_web_search(user_input)
            print(f"\nAgent > Here is what I found:\n{result}")

        elif "MEMORY" in intent:
            mem_context = search_memory(user_input)
            ans = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": f"Answer using this memory context:\n{mem_context}"},
                    {"role": "user", "content": user_input}
                ]
            )
            print(f"\nAgent > {ans.choices[0].message.content.strip()}")

        else:
            ans = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": user_input}
                ]
            )
            print(f"\nAgent > {ans.choices[0].message.content.strip()}")

if __name__ == "__main__":
    main()