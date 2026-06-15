import os
import re
import time
from playwright.sync_api import sync_playwright

STUBHUB_URL = "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/"
MY_BUDGET = 250

def run():
    print("🚀 Cloud Tracker: Isolating Seating Configurations...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            page.goto(STUBHUB_URL, timeout=60000)
            time.sleep(12) 
            
            raw_text = page.locator("body").text_content()
            
            print("\n================ WATCHMAN ALERTS ================")
            
            # This regex looks specifically for strings containing 'Section X Row Y' followed by a price symbol
            # Example: Section 324Row Z2 tickets together...$259
            pattern = r"Section\s*(\d+)\s*Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})"
            
            matches = re.findall(pattern, raw_text)
            
            match_count = 0
            for section, row, price_str in matches:
                price = int(price_str)
                print(f"📌 Detected: Section {section}, Row {row} -> ${price}")
                
                if price <= MY_BUDGET:
                    print(f"🚨 MATCH UNDER BUDGET: Section {section}, Row {row} is available for ${price}!")
                    match_count += 1
            
            if len(matches) == 0:
                print("⚠️ Text patterns did not cleanly slice. StubHub text layout may have shifted slightly.")
            elif match_count == 0:
                print(f"ℹ️ Scanned all visible listings. Current market baseline is above ${MY_BUDGET}.")
                
            print("=================================================")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
        browser.close()
    print("🏁 Loop complete.")

if __name__ == "__main__":
    run()
