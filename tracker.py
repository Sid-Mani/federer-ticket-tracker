import os
import re
import time
import requests
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth  

# Configuration
MY_BUDGET = 250
MAX_DISPLAY_PRICE = 350
DISCORD_WEBHOOK_URL = "" # Paste your Discord webhook link here if using

TRACKING_SITES = {
    "StubHub": "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/",
    "TickPick": "https://www.tickpick.com/buy-us-open-roger-federer-an-icon-returns-to-ny-tickets-arthur-ashe-stadium-8-25-26-7pm/8034802/"
}

def send_alert(site, section, row, price):
    msg = f"🚨 **FEDERER BUDGET ALERT!** 🚨\nFound a seat on **{site}** under budget!\nSection: {section} | Row: {row}\nPrice: **${price}**\nLink: {TRACKING_SITES[site]}"
    print(msg)
    if DISCORD_WEBHOOK_URL:
        try: requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
        except: print("⚠️ Failed to send Discord notification.")

def scan_site(page, name, url):
    print(f"\n🔍 Scanning {name}...")
    all_site_tickets = []
    try:
        page.goto(url, timeout=45000)
        time.sleep(12)
        
        # Pull text content strictly to avoid picking up raw code/CSS class strings
        raw_text = page.locator("body").text_content()
        tokens = [t.strip() for t in re.split(r'(\s+)', raw_text) if t.strip()]
        full_clean_text = " ".join(tokens)
        
        patterns = [
            r"(?:Section|Sec)\s*(\d+)[^\d]*?Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})",
            r"\$(\d{1,4}).*?(?:Section|Sec)\s*(\d+)[^\d]*?Row\s*([A-Za-z\d\-]+)"
        ]
        
        seen_tickets = set()
        
        for pattern in patterns:
            for match in re.finditer(pattern, full_clean_text, re.IGNORECASE):
                if pattern == patterns[0]:
                    sec_num, row_num, price_str = match.group(1), match.group(2), match.group(3)
                else:
                    price_str, sec_num, row_num = match.group(1), match.group(2), match.group(3)
                
                price = int(price_str)
                ticket = parse_valid_ticket(sec_num, row_num, price, seen_tickets)
                if ticket: 
                    all_site_tickets.append(ticket)
        
        # Sort primarily by Row Letter (A-Z) and secondarily by lowest price
        sorted_tickets = sorted(all_site_tickets, key=lambda x: (x['row'], x['price']))
        
        for t in sorted_tickets:
            print(f"📊 [{name}] Section {t['section']}, Row {t['row']} -> ${t['price']}")
            if t['price'] <= MY_BUDGET:
                send_alert(name, t['section'], t['row'], t['price'])
                        
        print(f"✅ {name}: Successfully tracked {len(sorted_tickets)} verified listings.")
    except Exception as e:
        print(f"❌ {name} execution breakdown: {str(e)}")

def parse_valid_ticket(sec_num, row_num, price, seen_tickets):
    # Ensure it's a normal alphanumeric row indicator, filtering out accidental artifact strings
    if len(row_num) > 4 or "GAP" in row_num.upper():
        return None
        
    if 100 <= int(sec_num) <= 400:
        ticket_id = f"{sec_num}-{row_num}-{price}"
        if ticket_id not in seen_tickets and 100 <= price <= MAX_DISPLAY_PRICE:
            seen_tickets.add(ticket_id)
            return {"section": sec_num, "row": row_num.upper(), "price": price}
    return None

def run():
    print("🚀 Cloud Watchman Matrix: Active Automated Production Mode...")
    stealth = Stealth()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="en-US"
        )
        
        stealth.apply_stealth_sync(context)
        page = context.new_page()
        
        for name, url in TRACKING_SITES.items():
            scan_site(page, name, url)
            time.sleep(6)
            
        browser.close()
    print("🏁 Sweep complete.")

if __name__ == "__main__":
    run()
