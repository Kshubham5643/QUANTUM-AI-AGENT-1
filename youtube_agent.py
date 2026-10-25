import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def run_youtube(query):
    print(f"🚀 [DEBUG] run_youtube called with query: '{query}'")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        print("🌐 Initializing ChromeDriver via Manager...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        print("🌐 Opening YouTube...")
        driver.get("https://www.youtube.com")
        time.sleep(2)

        if query and query.lower() not in ["yt", "youtube", "none", ""]:
            print(f"⌨️ Searching for: {query}...")
            
            search_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)

            print("🖱️ Locating first video result...")
            first_video = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView(true);", first_video)
            time.sleep(1)
            
            try:
                first_video.click()
            except Exception:
                driver.execute_script("arguments[0].click();", first_video)
                
            print("▶️ Playing video successfully.")
        else:
            print("🏠 YouTube homepage opened.")

        input("\n✅ Done! Press [Enter] in this terminal to close the browser session...")
    except Exception as e:
        print(f"❌ Error during YouTube execution: {e}")
        input("\nPress [Enter] to exit...")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    query = ""
    if len(sys.argv) > 1 and sys.argv[1] and sys.argv[1].lower() != "none":
        query = " ".join(sys.argv[1:])
    run_youtube(query)