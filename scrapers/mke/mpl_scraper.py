from playwright.sync_api import sync_playwright
from dateutil import parser
from datetime import datetime, timedelta
import os
import sys

# Ensure we can import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from base_scraper import BaseScraper
from utils import get_next_week_date_range

class MplScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://mpl.libnet.info/events"

    def scrape(self):
        start_date, end_date = get_next_week_date_range()
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        all_found_events = []
        url = f"{self.base_url}?r=range&start={start_str}&end={end_str}"
        print(f"Fetching Milwaukee Public Library events from: {url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                
                # Wait for the events container to load
                try:
                    page.wait_for_selector('.eelistevent-data', timeout=15000)
                except Exception as e:
                    print(f"No events found or page timed out: {e}")
                    browser.close()
                    return []
                
                # Fetch all event elements
                events = page.query_selector_all('.eelistevent-data')
                
                for event in events:
                    title_elem = event.query_selector('.eelisttitle a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.inner_text().strip()
                    # The href might be relative, let's make it absolute
                    href = title_elem.get_attribute('href')
                    if href and href.startswith('/'):
                        event_url = "https://mpl.libnet.info" + href
                    else:
                        event_url = href or ""
                        
                    time_elem = event.query_selector('.eelisttime')
                    time_text = time_elem.inner_text().strip() if time_elem else ""
                    
                    venue_elem = event.query_selector('.eelocation')
                    venue = venue_elem.inner_text().strip() if venue_elem else ""
                    
                    desc_elem = event.query_selector('.eelistdesc')
                    description = desc_elem.inner_text().strip() if desc_elem else ""
                    
                    # Deduplicate
                    if any(e['title'] == title and e['url'] == event_url for e in all_found_events):
                        continue
                    
                    # Parse Date and Time
                    # e.g., "Monday, May 18: All Day" or "Monday, May 18: 6:00 PM - 7:00 PM"
                    event_datetime = start_date # default fallback
                    if time_text:
                        parts = time_text.split(":")
                        if len(parts) >= 2:
                            # "Monday, May 18"
                            date_part = parts[0].strip()
                            # "All Day" or " 6" (then the rest)
                            # Actually, if we split by ":", time might be " 6:00 PM - 7:00 PM" -> parts[1] is " 6"
                            # Better to split by first occurrence or just replace "All Day"
                            time_part = ":".join(parts[1:]).strip() 
                            
                            # Clean up time part (take first time if range)
                            if "All Day" in time_part:
                                clean_time = ""
                            else:
                                clean_time = time_part.split("-")[0].strip()
                                
                            full_date_str = f"{date_part} {start_date.year} {clean_time}".strip()
                            try:
                                parsed_dt = parser.parse(full_date_str, fuzzy=True)
                                event_datetime = parsed_dt
                            except Exception as e:
                                print(f"Could not parse date '{full_date_str}': {e}")
                                
                    all_found_events.append({
                        "title": title,
                        "date_time": event_datetime,
                        "venue": venue,
                        "url": event_url,
                        "description": f"Source: Milwaukee Public Library\n{description[:300]}..."
                    })
                    
                browser.close()
        except Exception as e:
            print(f"Error while scraping MPL: {e}")
            
        return all_found_events
