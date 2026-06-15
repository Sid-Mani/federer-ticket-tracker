import os
import json
import time
from playwright.sync_api import sync_playwright

STUBHUB_URL = "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/"
MY_BUDGET = 250

def run():
    print("🚀 Cloud Tracker: Targeting JSA Data Stream...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Intercept and process the data stream
        def handle_response(response):
            # Target the specific JSON API pipe you caught
            if "jsa/v1/events" in response.url:
                try:
                    data = response.json()
                    
                    # Target StubHub's listing data array inside the payload
                    # (Usually nested under 'items' or 'listings' inside their map object)
                    listings = data.get("items", []) or data.get("listings", []) or data.get("itemsList", [])
                    
                    print(f"\n🎯 FOUND RAW DATA FEED! Analyzing {len(listings)} active ticket groups...")
                    
                    match_count = 0
                    for ticket in listings:
                        # Extract exact details (handling various potential naming structures)
                        price = ticket.get("price", ticket.get("rawPrice", 9999))
                        row = ticket.get("row", ticket.get("rowName", "Unknown Row"))
                        section = ticket.get("section", ticket.get("sectionName", "Unknown Section"))
                        
                        if price <= MY_BUDGET:
                            print(f"🚨 IN BUDGET: Section {section}, Row {row} -> ${price}")
                            match_count += 1
                    
                    if match_count == 0:
                        print("ℹ️ Evaluated listings, but none are under budget right now.")
                        
                except Exception as e:
                    # If the data structure looks slightly different, dump a small preview so we can inspect it
                    try:
                        text_preview = response.text()[:300]
                        print(f"📡 Caught structure: {text_preview}")
                    except:
                        pass

        page.on("response", handle_response)
        
        print("🤖 Opening StubHub...")
        try:
            # We remove wait_until="networkidle" to prevent timeouts, and use a safe 45-second overall window
            page.goto(STUBHUB_URL, timeout=45000)
            print("⏳ Waiting for map layers to settle...")
            time.sleep(12) 
        except Exception as e:
            print(f"⚠️ Page navigation hit a limit, proceeding to process caught data...")
            
        browser.close()
    print("🏁 Loop complete.")

if __name__ == "__main__":
    run()
