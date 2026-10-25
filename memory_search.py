import os
from dotenv import load_dotenv
from groq import Groq
from supabase import create_client, Client

load_dotenv()

# Initialize API Clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_KEY")
)

query = input("\nWhat do you want to ask your agent's cloud memory? ")

print("\n☁️ Fetching past memories from Supabase...")
# Fetch recent memories from the table
try:
    response = supabase.table("agent_memories").select("user_goal, website_summary, created_at").order("created_at", desc=True).limit(5).execute()
    memories = response.data
except Exception as e:
    print(f"❌ Error fetching from Supabase: {e}")
    memories = []

if not memories:
    print("❌ No memories found in Supabase yet!")
else:
    # Format memories for the AI brain
    memory_context = ""
    for m in memories:
        memory_context += f"Goal: {m.get('user_goal')}\nSummary/Result:\n{m.get('website_summary')}\n---\n"

    print("\n🧠 AI is searching through past agent memories using gpt-oss-20b...")
    ai_response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system", 
                "content": "You are an AI assistant with access to the user's past agent execution memories stored in the cloud. Answer the user's question using ONLY the provided memory context."
            },
            {"role": "user", "content": f"Memory Context:\n{memory_context}\n\nQuestion: {query}"}
        ]
    )

    answer = ai_response.choices[0].message.content.strip()

    print("\n====================")
    print("CLOUD MEMORY RESULT")
    print("====================\n")
    print(answer)