import streamlit as st
import os

# --- IMPORT YOUR SEPARATE AGENT MODULES ---
# (Make sure these files are uploaded to your GitHub repo alongside app.py)
try:
    import youtube_agent
except ImportError:
    youtube_agent = None

try:
    import file_agent
except ImportError:
    file_agent = None

try:
    import duck_duck_agent
except ImportError:
    duck_duck_agent = None

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("### ⚡ System Navigation")
module_choice = st.sidebar.radio(
    "Choose Module:",
    ["Main Router", "YouTube Agent", "File Agent", "DuckDuckGo Agent"]
)

# --- ROUTING MODULES ---
if module_choice == "Main Router":
    st.subheader("🧠 Master Intent Router")
    st.info("QUANTUM core online. Give me a command!")
    # Your main router chat code...

elif module_choice == "YouTube Agent":
    st.subheader("🎬 YouTube Media Agent")
    if youtube_agent and hasattr(youtube_agent, "run"):
        youtube_agent.run()  # Calls the function inside your youtube_agent.py file
    else:
        st.error("youtube_agent.py file not found or missing 'run()' function in repository.")

elif module_choice == "File Agent":
    st.subheader("📁 File Agent")
    if file_agent and hasattr(file_agent, "run"):
        file_agent.run()
    else:
        st.warning("File agent module not detected.")

elif module_choice == "DuckDuckGo Agent":
    st.subheader("🔍 Search Agent")
    if duck_duck_agent and hasattr(duck_duck_agent, "run"):
        duck_duck_agent.run()
    else:
        st.warning("DuckDuckGo agent module not detected.")
