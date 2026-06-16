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
    "VividSeats": "https://www.vividseats.com/us-open-roger-federer---an-icon-returns-to-ny-tickets-arthur-ashe-stadium-8-25-2026--sports-tennis/production/7134771?quantity=2",
    "TickPick": "https://www.tickpick.com/buy-us-open-roger-federer-an-icon-returns-to-ny-tickets-arthur-ashe-stadium-8-25-26-7pm/8034802/",
    "SeatGeek": "https://seatgeek.com/us-open-tennis-tickets/tennis/2026-08-25-7-pm/18293103"
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
    seen_tickets = set()
    
    try:
        # Load the marketplace and allow scripts to fully unpack the interface
        page.goto(url, timeout=60000)
        time.sleep(15) 
        
        # Universal inner HTML extraction to read layout content regardless of DOM nesting structure
        raw_html = page.content()
        
        # Super-regex profiles capable of parsing broken text chunks, fees, and multi-line spans
        patterns = [
            r"(?:Section|Sec)\s*(\d+).*?Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})",
            r"\$(\d{1,4}).*?(?:Section|Sec)\s*(\d+).*?Row\s*([A-Za-z\d\-]+)",
            r"(?:Section|Sec)\s*(\d+)[^\d]*?\$(\d{1,4})" # Safety loop if a platform drops the Row string entirely
        ]
        
        # Scan data blocks
        for pattern in patterns:
            for match in re.finditer(pattern, raw_html, re.IGNORECASE | re.DOTALL):
                try:
                    if pattern == patterns[0]:
                        sec, row, prc = match.group(1), match.group(2), int(match.group(3))
                    elif pattern == patterns[1]:
                        prc, sec, row = int(match.group(1)), match.group(2), match.group(3)
                    else:
                        sec, row, prc = match.group(1), "ANY", int(match.group(2))
                        
                    # Filter and sanitize data fields
                    if 100 <= int(sec) <= 499 and 100 <= prc <= MAX_DISPLAY_PRICE:
                        ticket_id = f"{sec}-{row}-{prc}"
                        if ticket_id not in seen_tickets:
                            seen_tickets.add(ticket_id)
                            all_site_tickets.append({"section": sec, "row": row.upper(), "price": prc})
                except:
                    continue

        # Sort cleanly: Alphabetical by Row, then ascending by cheapest price
        sorted_tickets = sorted(all_site_tickets, key=lambda x: (x['row'], x['price']))
        
        for t in sorted_tickets:
            print(f"📊 [{name}] Section {t['section']}, Row {t['row']} -> ${t['price']}")
            if t['price'] <= MY_BUDGET:
                send_alert(name, t['section'], t['row'], t['price'])
                        
        print(f"✅ {name}: Successfully tracked {len(sorted_tickets)} verified listings.")
    except Exception as e:
        print(f"❌ {name} execution breakdown: {str(e)}")

def run():
    print("🚀 Cloud Watchman Matrix: Sorted Tracking Mode Active...")
    stealth = Stealth()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="en-US"
        )
        
        # Apply strict 2026 stealth specifications directly onto the synchronization layer
        stealth.apply_stealth_sync(context)
        page = context.new_page()
        
        for name, url in TRACKING_SITES.items():
            scan_site(page, name, url)
            time.sleep(8) # Space out requests to bypass bot firewalls naturally
            
        browser.close()
    print("🏁 Sweep complete.")

if __name__ == "__main__":
    run()
