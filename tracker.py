import os
import json
import time
from playwright.sync_api import sync_playwright

STUBHUB_URL = "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/"
MY_BUDGET = 250

def run():
    print("🚀 Cloud Tracker Started...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # This magic function listens to the background network data streams!
        def handle_response(response):
            # We look for StubHub's background data payload
            if "event" in response.url or "listings" in response.url:
                try:
                    # Parse the raw network data into clean Python text
                    data = response.json()
                    
                    # Dig into StubHub's data structure to find the ticket array
                    # Note: We'll fine-tune these exact keys once we catch the first payload
                    listings = data.get("items", []) or data.get("listings", [])
                    
                    print(f"📡 Found background data stream! Analyzing {len(listings)} listings...")
                    
                    for ticket in listings:
                        price = ticket.get("price", 9999)
                        row = ticket.get("row", "Unknown Row")
                        section = ticket.get("section", "Unknown Section")
                        
                        if price <= MY_BUDGET:
                            print(f"🚨 MATCH found! Section {section}, Row {row} is ${price}!")
                except Exception:
                    pass # Skip background files that aren't clean data

        # Tell the page to monitor background responses
        page.on("response", handle_response)
        
        print("🤖 Opening StubHub in the cloud...")
        page.goto(STUBHUB_URL)
        time.sleep(8) # Give the data streams plenty of time to finish loading
        
        browser.close()
    print("🏁 Loop complete.")

if __name__ == "__main__":
    run()
