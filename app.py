import subprocess
import sys

# If Linux doesn't have CREATE_NO_WINDOW, this dynamically creates a dummy attribute so it never crashes
if not hasattr(subprocess, 'CREATE_NO_WINDOW'):
    subprocess.CREATE_NO_WINDOW = 0
import streamlit as st
import subprocess
import sys
import os
import json
import urllib.parse
from pathlib import Path
import webbrowser
from groq import Groq
from dotenv import load_dotenv
import importlib.util

PLUGINS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
if not os.path.exists(PLUGINS_DIR):
    os.makedirs(PLUGINS_DIR)

def get_dynamic_plugins():
    """Scans the plugins folder for self-coded agent modules."""
    plugins = {}
    if os.path.exists(PLUGINS_DIR):
        for f in os.listdir(PLUGINS_DIR):
            if f.endswith(".py") and f != "__init__":
                plugin_name = f[:-3]
                plugins[plugin_name] = os.path.join(PLUGINS_DIR, f)
    return plugins

load_dotenv()

st.set_page_config(
    page_title="QUANTUM // AI Command Core",
    page_icon="🌌",
    layout="wide"
)

# Glassmorphic UI Styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: radial-gradient(circle at 50% 20%, #2e1065 0%, #0f071e 50%, #030008 100%); color: #f3f4f6; }
    header, #MainMenu, footer { visibility: hidden; }
    [data-testid="stSidebar"] { background-color: rgba(18, 10, 30, 0.65); backdrop-filter: blur(25px); border-right: 1px solid rgba(168, 85, 247, 0.15); }
    .stTextInput>div>div>input { background-color: rgba(255, 255, 255, 0.04) !important; border: 1px solid rgba(168, 85, 247, 0.2) !important; color: #ffffff !important; border-radius: 14px; }
    .stButton>button { border-radius: 14px; font-weight: 600; background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(255, 255, 255, 0.02)); border: 1px solid rgba(168, 85, 247, 0.3); color: #f3f4f6; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white; font-weight: 700;'>Q U A N T U M</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #c084fc;'>AUTONOMOUS MODULAR DESKTOP AGENT</p>", unsafe_allow_html=True)

def get_file_catalog():
    # Expands scope to your entire user profile folders
    home_dir = os.path.expanduser("~") 
    target_dirs = [
        os.path.join(home_dir, "Desktop"),
        os.path.join(home_dir, "Documents"),
        os.path.join(home_dir, "Downloads")
    ]
    
    catalog = {}
    for d in target_dirs:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                for file in files:
                    catalog[file] = os.path.join(root, file)
                    
    return catalog

# Sidebar Auth & Nav
st.sidebar.header("🔑 Authentication")
groq_api_key_input = st.sidebar.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))

st.sidebar.markdown("---")
st.sidebar.header("⚡ System Navigation")
tool = st.sidebar.radio("Choose Module:", ["Main Router", "YouTube Agent", "File Agent", "DuckDuckGo Agent"])

def get_groq_client():
    api_key = groq_api_key_input or os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ Please provide your Groq API Key.")
        return None
    return Groq(api_key=api_key)

if tool == "Main Router":
    st.header("🧠 Master Intent Router")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "QUANTUM core online. Give me a command!"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Command the agent..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        client = get_groq_client()
        if client:
            try:
                file_catalog = get_file_catalog()
                plugins = get_dynamic_plugins()

                # Define native tools including plugin execution
                # Define native tools for function calling
                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": "execute_action",
                            "description": "Execute standard desktop or browser actions like YouTube, DuckDuckGo, Maps, or opening files.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "enum": ["youtube", "duckduckgo", "maps", "open_file"],
                                        "description": "The type of action to perform."
                                    },
                                    "target": {
                                        "type": "string",
                                        "description": "The search query, place name, or file description."
                                    }
                                },
                                "required": ["action", "target"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "create_plugin",
                            "description": "Write and save a brand-new Python plugin script. RULES: 1. If it's a data/utility script, write output to a text file and open it using os.startfile. 2. If it's a visual app, use tkinter.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "plugin_name": {
                                        "type": "string",
                                        "description": "Short snake_case filename for the plugin (e.g. pdf_list)."
                                    },
                                    "code": {
                                        "type": "string",
                                        "description": "Full, executable Python 3 code string."
                                    },
                                    "arg": {
                                        "type": "string",
                                        "description": "Optional argument to pass when executing the script."
                                    }
                                },
                                "required": ["plugin_name", "code"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "run_plugin",
                            "description": "Execute an already existing dynamic plugin from the plugins folder by its exact name.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "plugin_name": {
                                        "type": "string",
                                        "description": "The exact name of the plugin script to run (without .py, e.g. pdf_list)."
                                    },
                                    "arg": {
                                        "type": "string",
                                        "description": "Optional argument or input for the plugin."
                                    }
                                },
                                "required": ["plugin_name"]
                            }
                        }
                    }
                ]

                system_prompt = (
                    "You are QUANTUM, an advanced autonomous desktop assistant built for Shubham Kumar. "
                    f"Available File Context: {json.dumps(file_catalog)}. "
                    f"Available Dynamic Plugins Built So Far: {list(plugins.keys())}. "
                    "If the user wants to use a previously created plugin, use `run_plugin`. If they want a brand-new tool, use `create_plugin`."
                )

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": system_prompt}, 
                        {"role": "user", "content": prompt}
                    ],
                    tools=tools,
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                agent_replies = []
                base_dir = os.path.dirname(os.path.abspath(__file__))

                if response_message.tool_calls:
                    has_executed = False
                    for tool_call in response_message.tool_calls:
                        fn_name = tool_call.function.name
                        fn_args = json.loads(tool_call.function.arguments)

                        if fn_name == "execute_action":
                            has_executed = True
                            action = fn_args.get("action")
                            target = fn_args.get("target", "")

                            if action == "youtube":
                                agent_replies.append(f"🚀 Opening YouTube tab for: **{target or 'lofi music'}**")
                                webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(target or 'lofi music')}")
                            elif action == "duckduckgo":
                                agent_replies.append(f"🦆 Searching DuckDuckGo for: **{target}**")
                                webbrowser.open(f"https://duckduckgo.com/?q={urllib.parse.quote(target)}")
                            elif action == "open_file":
                                agent_replies.append(f"📂 Locating and opening: **{target}**")
                                subprocess.Popen([sys.executable, os.path.join(base_dir, "file_agent.py"), target], creationflags=subprocess.CREATE_NO_WINDOW)
                            elif action == "maps":
                                agent_replies.append(f"🗺️ Opening Google Maps for: **{target}**")
                                webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(target)}")

                        elif fn_name == "create_plugin":
                            has_executed = True
                            p_name = fn_args.get("plugin_name", "custom_task")
                            p_code = fn_args.get("code", "")
                            p_arg = fn_args.get("arg", "")
                            
                            plugin_file = os.path.join(PLUGINS_DIR, f"{p_name}.py")
                            with open(plugin_file, "w", encoding="utf-8") as pf:
                                pf.write(p_code)
                            
                            agent_replies.append(f"🧬 **Self-Evolution Activated**: Successfully coded, saved, and executed `{p_name}.py`!")
                            subprocess.Popen([sys.executable, plugin_file, p_arg], creationflags=subprocess.CREATE_NO_WINDOW)

                        elif fn_name == "run_plugin":
                            has_executed = True
                            p_name = fn_args.get("plugin_name")
                            p_arg = fn_args.get("arg", "")
                            
                            if p_name in plugins:
                                plugin_file = plugins[p_name]
                                agent_replies.append(f"⚡ **Executing Plugin**: Running `{p_name}.py`...")
                                subprocess.Popen([sys.executable, plugin_file, p_arg], creationflags=subprocess.CREATE_NO_WINDOW)
                            else:
                                agent_replies.append(f"⚠️ Plugin `{p_name}` not found in registry.")

                    if has_executed:
                        st.session_state["last_action_prompt"] = prompt
                else:
                    agent_replies.append(response_message.content or "How else can I help you?")

                final_reply = "\n\n".join(agent_replies)
                st.chat_message("assistant").markdown(final_reply)
                st.session_state.messages.append({"role": "assistant", "content": final_reply})

            except Exception as e:
                err_msg = f"⚠️ Router Error: {str(e)}"
                st.chat_message("assistant").markdown(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})

elif tool == "YouTube Agent":
    st.header("📺 YouTube Sub-Agent")
    q = st.text_input("Query:")
    if st.button("Launch"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        yt_path = os.path.join(base_dir, "youtube_agent.py")
        subprocess.Popen([sys.executable, yt_path, q], creationflags=subprocess.CREATE_NEW_CONSOLE)

elif tool == "File Agent":
    st.header("📂 File Sub-Agent Manager")
    st.json(get_file_catalog())
    f_query = st.text_input("File name or number (e.g. 1, last download):")
    if st.button("Open File"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "file_agent.py")
        subprocess.Popen([sys.executable, file_path, f_query], creationflags=subprocess.CREATE_NEW_CONSOLE)

elif tool == "DuckDuckGo Agent":
    st.header("🦆 DuckDuckGo Search Agent")
    ddg_query = st.text_input("Search query:")
    if st.button("Search Web"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ddg_path = os.path.join(base_dir, "duckduck_agent.py")
        subprocess.Popen([sys.executable, ddg_path, ddg_query], creationflags=subprocess.CREATE_NEW_CONSOLE)
