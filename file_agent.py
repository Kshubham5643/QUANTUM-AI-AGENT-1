import sys
import os
from pathlib import Path

def find_and_open_file(query):
    if not query:
        print("❌ No file specified.")
        return

    query_lower = query.lower()
    print(f"🔍 Searching system for file matching: '{query}'...")

    home = Path.home()
    search_dirs = [
        home / "Downloads",
        home / "Documents",
        home / "Desktop",
        home / "Pictures",
        home / "Pictures" / "Screenshots",
        Path.cwd(),
        Path.cwd() / "uploads"
    ]

    candidates = []
    for d in search_dirs:
        if d.exists() and d.is_dir():
            for root, dirs, files in os.walk(d):
                if any(p.startswith('.') for p in Path(root).parts):
                    continue
                for f in files:
                    if f.lower().endswith(('.ini', '.py', '.bat', '.json')):
                        continue
                    full_path = os.path.join(root, f)
                    candidates.append((f, full_path))

    # Handle specialized queries like "latest screenshot"
    if "latest screenshot" in query_lower or ("screenshot" in query_lower and "latest" in query_lower):
        screenshot_dir = home / "Pictures" / "Screenshots"
        if screenshot_dir.exists():
            ss_files = list(screenshot_dir.glob("*.*"))
            if ss_files:
                latest_ss = max(ss_files, key=os.path.getmtime)
                print(f"📷 Opening latest screenshot: {latest_ss}")
                os.startfile(str(latest_ss))
                input("\nPress [Enter] to exit...")
                return

    # Exact or substring match across all collected files
    best_match = None
    for fname, fpath in candidates:
        if query_lower in fname.lower():
            best_match = fpath
            break

    # Fallback: check if all words in query appear in filename
    if not best_match:
        query_words = query_lower.split()
        for fname, fpath in candidates:
            if all(word in fname.lower() for word in query_words):
                best_match = fpath
                break

    if best_match:
        print(f"📂 Opening: {best_match}")
        os.startfile(best_match)
    else:
        print(f"❌ Could not find any file matching '{query}'.")
    
    input("\nPress [Enter] to exit...")

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    find_and_open_file(q)