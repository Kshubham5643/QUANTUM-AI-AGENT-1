import sys
import urllib.parse
import webbrowser

def run_duckduckgo(query):
    if not query or query.lower() in ["none", ""]:
        query = "latest tech news"
    
    print(f"🦆 Searching DuckDuckGo for: '{query}'")
    search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
    webbrowser.open(search_url)
    print("✅ DuckDuckGo search opened in browser.")

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    run_duckduckgo(q)