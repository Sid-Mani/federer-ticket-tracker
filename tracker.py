import os
import json
import time
from playwright.sync_api import sync_playwright

STUBHUB_URL = "https://www.stubhub.com/roger-federer-flushing-tickets-8-25-2026/event/161318967/"

def run():
    print("🚀 Cloud Tracker Diagnostic Mode Started...")
    
    with sync_playwright() as p:
        # We add an argument here to look like a normal desktop user so we don't get blocked
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Print out the URL of every background Fetch/XHR data request that happens
        def handle_response(response):
            request_type = response.request.resource_type
            if request_type in ["fetch", "xhr"]:
                print(f"📡 Caught Data Stream URL: {response.url[:120]}...") # truncate if too long

        page.on("response", handle_response)
        
        print("🤖 Opening StubHub...")
        page.goto(STUBHUB_URL, wait_until="networkidle") # Wait until the network goes completely quiet
        time.sleep(5) 
        
        browser.close()
    print("🏁 Diagnostic Loop complete.")

if __name__ == "__main__":
    run()
