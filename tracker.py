import os
import re
import time
from playwright.sync_api import sync_playwright

STUBHUB_URL = "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/"
MY_BUDGET = 250

def run():
    print("🚀 Cloud Tracker: Extracting Row and Seating Data...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            page.goto(STUBHUB_URL, timeout=60000)
            print("⏳ Page loaded. Parsing visible elements...")
            time.sleep(12) # Give the listings plenty of time to populate fully
            
            # Extract clean text blocks from the webpage
            raw_text = page.locator("body").text_content()
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
            
            print("\n---------------- WATCHMAN REPORT ----------------")
            
            # Look through lines to tie prices together with their matching Row/Section
            for i, line in enumerate(lines):
                # Search for any string that contains a dollar sign
                if "$" in line:
                    # Regular expression to extract just the main digits before a decimal point (e.g., $259.00 -> 259)
                    price_match = re.search(r'\$(\d{1,4})', line)
                    if price_match:
                        current_price = int(price_match.group(1))
                        
                        # Grab a window of 4 lines around the price to capture the Section and Row numbers
                        start_window = max(0, i - 3)
                        end_window = min(len(lines), i + 3)
                        surrounding_context = " | ".join(lines[start_window:end_window])
                        
                        # Print EVERYTHING it finds right now so we can see the exact layout
                        print(f"💰 Found Ticket: ${current_price} -> Context: {surrounding_context}")
                        
                        # If it hits our budget target, drop an alert!
                        if current_price <= MY_BUDGET:
                            print(f"🚨 ALERT: THIS ONE IS IN BUDGET! (${current_price})")
                            
            print("-------------------------------------------------")
            
        except Exception as e:
            print(f"❌ Automation encountered an error: {str(e)}")
            
        browser.close()
    print("🏁 Loop complete.")

if __name__ == "__main__":
    run()
