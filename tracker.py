import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

MY_BUDGET = 250
# Paste your Discord Webhook URL here if you want phone alerts, or leave it as ""
DISCORD_WEBHOOK_URL = "" 

TRACKING_SITES = {
    "StubHub": "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/",
    "VividSeats": "https://www.vividseats.com/us-open-roger-federer---an-icon-returns-to-ny-tickets-arthur-ashe-stadium-8-25-2026--sports-tennis/production/7134771?quantity=2&maxPrice=404&currency=USD",
    "TickPick": "https://www.tickpick.com/buy-us-open-roger-federer-an-icon-returns-to-ny-tickets-arthur-ashe-stadium-8-25-26-7pm/8034802/"
}

def send_alert(site, section, row, price):
    msg = f"🚨 **FEDERER TICKET ALERT!** 🚨\nFound a seat on **{site}** under budget!\nSection: {section} | Row: {row}\nPrice: **${price}**\nLink: {TRACKING_SITES[site]}"
    print(msg)
    if DISCORD_WEBHOOK_URL:
        try: requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
        except: print("⚠️ Failed to send Discord notification.")

def scan_site(page, name, url):
    print(f"\n🔍 Scanning {name}...")
    try:
        page.goto(url, timeout=45000)
        time.sleep(10)
        
        raw_text = page.locator("body").text_content()
        tokens = [t.strip() for t in re.split(r'(\s+)', raw_text) if t.strip()]
        full_clean_text = " ".join(tokens)
        
        section_matches = list(re.finditer(r"(?:Section|Sec)\s*(\d+)", full_clean_text))
        seen_tickets = set()
        
        for index, match in enumerate(section_matches):
            start_pos = match.start()
            end_pos = section_matches[index+1].start() if index + 1 < len(section_matches) else len(full_clean_text)
            text_chunk = full_clean_text[start_pos:end_pos]
            
            sec_num = match.group(1)
            
            # Make sure it's a real Arthur Ashe upper/lower tier section number
            if not (100 <= int(sec_num) <= 140 or 200 <= int(sec_num) <= 240 or 300 <= int(sec_num) <= 340):
                continue
                
            row_match = re.search(r"Row\s*([A-Za-z\d\-]+)", text_chunk)
            row_num = row_match.group(1) if row_match else "Unknown"
            
            price_match = re.search(r'\$(\d{1,4})', text_chunk)
            if price_match:
                price = int(price_match.group(1))
                ticket_id = f"{sec_num}-{row_num}-{price}"
                
                # Filter out obvious structural layout glitches below $100
                if ticket_id not in seen_tickets and price >= 100:
                    seen_tickets.add(ticket_id)
                    print(f"📊 [{name}] Section {sec_num}, Row {row_num} -> ${price}")
                    
                    if price <= MY_BUDGET:
                        send_alert(name, sec_num, row_num, price)
                        
        print(f"✅ {name}: Successfully tracked {len(seen_tickets)} verified listings.")
    except Exception as e:
        print(f"❌ {name} execution hitch: {str(e)}")

def run():
    print("🚀 Cloud Watchman Matrix: Live Tracking Mode...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        for name, url in TRACKING_SITES.items():
            scan_site(page, name, url)
            time.sleep(5)
            
        browser.close()
    print("🏁 Sweep complete.")

if __name__ == "__main__":
    run()
