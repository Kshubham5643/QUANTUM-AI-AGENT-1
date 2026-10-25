import sys
import urllib.parse
import webbrowser
import streamlit as st

# Inside your search tool handler function:
def handle_duckduckgo_search(query):
    # (Your existing search logic that fetches the results...)
    results = search_duckduckgo(query) 
    
    # Display the results nicely in the Streamlit UI
    st.markdown("### 🔍 Search Results:")
    for item in results:
        title = item.get("title", "Link")
        url = item.get("href", "#")
        snippet = item.get("body", "")
        
        # Render a clean, clickable markdown link with its snippet
        st.markdown(f"- **[{title}]({url})**\n  > {snippet}")

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    run_duckduckgo(q)
