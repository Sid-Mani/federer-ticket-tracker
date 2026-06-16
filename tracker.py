import os
import re
import time
from playwright.sync_api import sync_playwright

MY_BUDGET = 250

# The master tracking list of all targeted platforms
TRACKING_SITES = {
    "StubHub": {
        "url": "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/",
        "pattern": r"Section\s*(\d+)\s*Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})"
    },
    "SeatGeek": {
        "url": "https://seatgeek.com/us-open-tennis-tickets/tennis/2026-08-25-7-pm/18293103?dd_referrer=https://www.google.com/&quantity=2",
        "pattern": r"(?:Section|Sec)\s*(\d+)\s*Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})|\$(\d{1,4}).*?(?:Section|Sec)\s*(\d+)\s*Row\s*([A-Za-z\d\-]+)"
    },
    "VividSeats": {
        "url": "https://www.vividseats.com/us-open-roger-federer---an-icon-returns-to-ny-tickets-arthur-ashe-stadium-8-25-2026--sports-tennis/production/7134771?quantity=2&maxPrice=404&currency=USD",
        "pattern": r"Section\s*(\d+)\s*Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})"
    },
    "TickPick": {
        "url": "https://www.tickpick.com/buy-us-open-roger-federer-an-icon-returns-to-ny-tickets-arthur-ashe-stadium-8-25-26-7pm/8034802/",
        "pattern": r"(\d+)\s*Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})|Section\s*(\d+).*?\$(\d{1,4})"
    },
    "EventTicketsCenter": {
        "url": "https://www.eventticketscenter.com/us-open-roger-federer-an-icon-returns-to-ny-flushing-08-25-2026/8034802/t",
        "pattern": r"Section\s*(\d+)\s*Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})"
    },
    "AXS": {
        "url": "https://tix.axs.com/qyNwCQAAAAD86qvUAAAAAABU%2fv%2f%2fwD%2f%2f%2f%2f%2fBXRoZW1lAP%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f/shop/marketplace?axssid=token_f9a8911be9e7&locale=en-US",
        "pattern": r"Sec\s*(\d+)\s*,?\s*Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})|(\d+)\s*Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})"
    },
    "Ticketmaster": {
        "url": "https://www.ticketmaster.com/us-open-roger-federer-an-icon-flushing-new-york-08-25-2026/event/1D0064C29B607BA2",
        "pattern": r"Sec\s*(\d+).*?Row\s*([A-Za-z\d\-]+).*?\$(\d{1,4})|Sec\s*(\d+).*?\$(\d{1,4})"
    }
}

def scan_site(page, name, config):
    print(f"\n🔍 Navigating to {name}...")
    try:
        page.goto(config["url"], timeout=45000)
        time.sleep(8) # Let the JavaScript elements load text contents
        
        raw_text = page.locator("body").text_content()
        tokens = [t.strip() for t in re.split(r'(\s+)', raw_text) if t.strip()]
        full_clean_text = " ".join(tokens)
        
        # Pull separate section matching indices
        section_matches = list(re.finditer(r"(?:Section|Sec)\s*(\d+)", full_clean_text))
        
        if not section_matches:
            # Fallback to look for raw numbers if the platform doesn't print the word "Section"
            section_matches = list(re.finditer(r"\b(\d{3})\b", full_clean_text))
            
        match_count = 0
        seen_tickets = set() # Avoid printing duplicate tracking artifacts
        
        for index, match in enumerate(section_matches):
            start_pos = match.start()
            end_pos = section_matches[index+1].start() if index + 1 < len(section_matches) else len(full_clean_text)
            text_chunk = full_clean_text[start_pos:end_pos]
            
            # Extract section number cleanly
            sec_num = match.group(1)
            
            # Find the row letter inside the isolated text chunk
            row_match = re.search(r"Row\s*([A-Za-z\d\-]+)", text_chunk)
            row_num = row_match.group(1) if row_match else "Unknown"
            
            # Extract the listing price inside the isolated text chunk
            price_match = re.search(r'\$(\d{1,4})', text_chunk)
            
            if price_match:
                price = int(price_match.group(1))
                ticket_id = f"{sec_num}-{row_num}-{price}"
                
                if ticket_id not in seen_tickets and price > 50: # filter out layout glitch numbers under $50
                    seen_tickets.add(ticket_id)
                    print(f"📊 [{name}] Section {sec_num}, Row {row_num} -> ${price}")
                    
                    if price <= MY_BUDGET:
                        print(f"🚨 ALERT: [{name}] MATCH FOUND! ${price}")
                        match_count += 1
                        
        if len(seen_tickets) == 0:
            print(f"⚠️ {name}: Text structure shifted or firewall active. Captured 0 readable ticket components.")
        else:
            print(f"✅ {name}: Scanned {len(seen_tickets)} unique ticket blocks layout profiles.")
            
    except Exception as e:
        print(f"❌ {name} navigation failed or timed out: {str(e)}")

def run():
    print("🚀 Cloud Watchman Master Grid: Active Strategy Engaged...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        print("================ WATCHMAN MATRIX MASTER REPORT ================")
        for site_name, site_config in TRACKING_SITES.items():
            scan_site(page, site_name, site_config)
            time.sleep(3) # Safe buffer pacing between sites to prevent automated block signatures
        print("===============================================================")
        
        browser.close()
    print("🏁 Master Grid Loop complete.")

if __name__ == "__main__":
    run()
