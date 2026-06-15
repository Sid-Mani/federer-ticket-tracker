import os
import json
import time
from playwright.sync_api import sync_playwright

STUBHUB_URL = "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/"

def run():
    print("🚀 Cloud Tracker: Extracting JSA Keys...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        def handle_response(response):
            # Let's catch anything coming from their JSA endpoint
            if "jsa/v1/events" in response.url:
                try:
                    data = response.json()
                    print("\n🔑 --- FOUND RAW JSA STREAM ---")
                    print(f"URL: {response.url[:80]}...")
                    # Print out the top-level keys so we can see how StubHub structures their data object
                    print(f"Top-level keys in this JSON: {list(data.keys())}")
                    
                    # If there's an 'event' or 'grid' object inside, show its keys too
                    for key in ['event', 'catalog', 'grid', 'data']:
                        if key in data and isinstance(data[key], dict):
                            print(f"Keys inside '{key}': {list(data[key].keys())}")
                    print("---------------------------------\n")
                except Exception as e:
                    print(f"⚠️ Found JSA stream but failed to read keys: {str(e)}")

        page.on("response", handle_response)
        
        print("🤖 Opening StubHub...")
        try:
            page.goto(STUBHUB_URL, timeout=45000)
            print("⏳ Waiting for data packets...")
            time.sleep(15) 
        except Exception as e:
            print(f"⚠️ Page hit limit, checking captured frames...")
            
        browser.close()
    print("🏁 Loop complete.")

if __name__ == "__main__":
    run()
