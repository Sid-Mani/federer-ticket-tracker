import os
import re
import time
from playwright.sync_api import sync_playwright

STUBHUB_URL = "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/"
MY_BUDGET = 250

def run():
    print("🚀 Cloud Tracker: Running Bulletproof Text Scan...")
    
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
            
            # Clean up the text layout into distinct words/phrases
            tokens = [t.strip() for t in re.split(r'(\s+)', raw_text) if t.strip()]
            full_clean_text = " ".join(tokens)
            
            print("\n================ WATCHMAN ALERTS ================")
            
            # Find every instance of a Section configuration on the page
            section_matches = list(re.finditer(r"Section\s*(\d+)\s*Row\s*([A-Za-z\d\-]+)", full_clean_text))
            
            match_count = 0
            for index, match in enumerate(section_matches):
                section = match.group(1)
                row = match.group(2)
                
                # Determine where this seat profile ends and the next one begins
                start_pos = match.start()
                end_pos = section_matches[index+1].start() if index + 1 < len(section_matches) else len(full_clean_text)
                
                # Isolate the exact chunk of text dedicated to this specific seat listing
                text_chunk = full_clean_text[start_pos:end_pos]
                
                # Search for the dollar amount inside this isolated ticket block
                price_match = re.search(r'\$(\d{1,4})', text_chunk)
                if price_match:
                    price = int(price_match.group(1))
                    print(f"📌 Ticket Target: Section {section}, Row {row} -> ${price}")
                    
                    if price <= MY_BUDGET:
                        print(f"🚨 MATCH UNDER BUDGET! Section {section}, Row {row} is ${price}!")
                        match_count += 1
                        
            if not section_matches:
                print("⚠️ Could not read seating components from the text layout layer.")
            elif match_count == 0:
                print(f"ℹ️ Scanned all {len(section_matches)} visible layout blocks. No seats under ${MY_BUDGET} yet.")
                
            print("=================================================")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
        browser.close()
    print("🏁 Loop complete.")

if __name__ == "__main__":
    run()
