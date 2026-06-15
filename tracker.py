import os
import time
from playwright.sync_api import sync_playwright

STUBHUB_URL = "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/"
MY_BUDGET = 250

def run():
    print("🚀 Cloud Tracker: Initiating Visual Scan Mode...")
    
    with sync_playwright() as p:
        # Launch a stealthy browser profile to avoid firewall flags
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        print("🤖 Opening StubHub event page...")
        try:
            page.goto(STUBHUB_URL, timeout=60000)
            print("⏳ Page loaded. Waiting 10 seconds for ticket listings to render text...")
            time.sleep(10)
            
            # Extract the raw visible text of the entire webpage layout
            raw_text = page.locator("body").text_content()
            
            print("\n🔍 Scanning page text for budget matches...")
            
            # Break down the text block into individual lines
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
            
            # Diagnostic: Let's see if we successfully bypassed the block and found prices
            price_lines = [l for l in lines if "$" in l]
            print(f"📊 Total price elements detected on screen: {len(price_lines)}")
            
            # Iterate through lines to print out prices and contextual seating info
            for i, line in enumerate(lines):
                if "$" in line:
                    try:
                        # Clean up the text to extract the raw number value
                        clean_price = int("".join(filter(str.isdigit, line)))
                        
                        if clean_price <= MY_BUDGET:
                            # Let's peek 2 lines before and after this price to pull Section/Row context
                            context_snippet = " | ".join(lines[max(0, i-2):i+3])
                            print(f"🚨 MATCH FOUND: ${clean_price} -> Context: {context_snippet}")
                    except ValueError:
                        pass
                        
            if not price_lines:
                print("⚠️ No prices found on the page text block. Page layout may have been throttled.")
                
        except Exception as e:
            print(f"❌ Automation encountered an error: {str(e)}")
            
        browser.close()
    print("🏁 Loop complete.")

if __name__ == "__main__":
    run()
