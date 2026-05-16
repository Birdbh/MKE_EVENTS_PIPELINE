import requests
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime, timedelta
import time

from base_scraper import BaseScraper
from utils import get_next_week_date_range

class VisitMKEScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://www.visitmilwaukee.org/events/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape(self):
        start_date, end_date = get_next_week_date_range()
        
        all_found_events = []
        
        # Simpleview usually paginates by 10 or 25. The user mentioned skip=10.
        # We will loop through a few pages to get the upcoming week.
        for skip in range(0, 50, 10):
            params = {
                "skip": skip,
                "bounds": "false",
                "view": "grid",
                "sort": "date",
                "filter_daterange[start]": start_date.strftime("%Y-%m-%d"),
                "filter_daterange[end]": end_date.strftime("%Y-%m-%d")
            }
            
            print(f"Fetching Visit MKE events (skip={skip})...")
            try:
                response = requests.get(self.base_url, headers=self.headers, params=params, timeout=15)
                response.raise_for_status()
            except Exception as e:
                print(f"Request failed for skip={skip}: {e}")
                break
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # The user specifically noted that each event is a 'section' with 'data-type="events"'
            listings = soup.find_all("section", {"data-type": "events"})
            
            # Fallback if the data-type attribute isn't present in the raw HTML (e.g. if it's JS-injected)
            # but we still want to try to find items in the known container
            if not listings:
                container = soup.find(class_="contentRender_name_plugins_events_layout_list")
                if container:
                    listings = container.select(".item, .listing, .event-item")

            if not listings:
                print(f"No listings found on page with skip={skip}")
                # If we find nothing on the first page, we might be hitting a wall.
                # But if we found things on skip=0 and nothing on skip=10, we're done.
                if skip > 0:
                    break
                else:
                    # One last desperate attempt: any h3 with a link that isn't in the footer/nav
                    main_content = soup.find("main") or soup.find("body")
                    listings = [h3.find_parent() for h3 in main_content.find_all("h3") if h3.find("a")]

            page_events_count = 0
            for listing in listings:
                # Based on user feedback: "contents or further links to click to get more details should be under that"
                title_tag = listing.find(["h3", "h2", "h4", "a"], class_=lambda x: x and ("title" in x or "name" in x))
                if not title_tag:
                    title_tag = listing.find("h3") or listing.find("a")
                
                if not title_tag:
                    continue
                    
                title = title_tag.text.strip()
                if not title or len(title) < 3:
                    continue
                
                # Link extraction
                link_tag = listing.find("a", href=True)
                link = link_tag["href"] if link_tag else self.base_url
                if link.startswith("/"):
                    link = "https://www.visitmilwaukee.org" + link
                    
                # Date extraction
                date_text = ""
                date_tag = listing.find(class_=lambda x: x and ("date" in x or "time" in x))
                if date_tag:
                    date_text = date_tag.text.strip()
                
                venue_text = ""
                venue_tag = listing.find(class_=lambda x: x and ("venue" in x or "location" in x or "place" in x))
                if venue_tag:
                    venue_text = venue_tag.text.strip()
                
                # Attempt to parse date
                try:
                    if date_text:
                        # Clean up common prefixes
                        clean_date = re.sub(r'^(Starts|Ends|On)\s+', '', date_text, flags=re.I)
                        event_datetime = parser.parse(clean_date, fuzzy=True)
                    else:
                        event_datetime = start_date
                except Exception:
                    event_datetime = start_date
                
                # Avoid duplicates
                if any(e['title'] == title and e['url'] == link for e in all_found_events):
                    continue
                    
                all_found_events.append({
                    "title": title,
                    "date_time": event_datetime,
                    "venue": venue_text,
                    "url": link,
                    "description": f"Source: Visit Milwaukee | Raw Date: {date_text}"
                })
                page_events_count += 1
            
            print(f"Found {page_events_count} new events on this page.")
            if page_events_count == 0:
                break
                
            # Be nice to the server
            time.sleep(1)
            
        return all_found_events

import re # needed for the lambda and regex inside the class
