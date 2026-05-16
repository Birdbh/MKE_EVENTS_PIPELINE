import cloudscraper
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime, timedelta
import re
import os
import sys

# Ensure we can import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from base_scraper import BaseScraper
from utils import get_next_week_date_range

class NorthShoreScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://discoverthenorthshoremke.com/discover-events-calendar/"
        self.scraper = cloudscraper.create_scraper()

    def scrape(self):
        start_date, end_date = get_next_week_date_range()
        all_found_events = []
        
        # This site does not use URL parameters for date filtering. 
        # We fetch the main events calendar page which lists upcoming events.
        print(f"Fetching North Shore events from: {self.base_url}")
        try:
            response = self.scraper.get(self.base_url)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch North Shore events page: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        events = soup.find_all('div', class_='ecs-event')
        
        for event in events:
            # Title & URL
            title_tag = event.find('h2', class_='entry-title')
            if not title_tag:
                continue
                
            link_tag = title_tag.find('a')
            if not link_tag:
                continue
                
            title = link_tag.text.strip()
            event_url = link_tag.get('href', '')
            
            # Deduplicate
            if any(e['title'] == title and e['url'] == event_url for e in all_found_events):
                continue
            
            # Date and Time
            date_tag = event.find(class_='decm_date')
            time_tag = event.find(class_='decm_time')
            
            event_datetime = start_date # default
            
            if date_tag:
                date_str = date_tag.text.strip()
                # If date is a range like "May 14 - 17, 2026", we take the first part
                # Wait, "May 14 - 17, 2026" split by "-" is "May 14 " and " 17, 2026"
                if "-" in date_str:
                    parts = [p.strip() for p in date_str.split("-")]
                    # extract year from the end if available
                    year_match = re.search(r'\d{4}', date_str)
                    year_str = year_match.group(0) if year_match else str(start_date.year)
                    # "May 14" + " 2026"
                    clean_date_str = f"{parts[0]} {year_str}"
                else:
                    clean_date_str = date_str
                
                time_str = ""
                if time_tag:
                    raw_time = time_tag.text.strip()
                    if "All Day" not in raw_time:
                        # Time might be "7:00 pm - 9:00 pm", take the first part
                        time_str = raw_time.split("-")[0].strip()
                        
                full_date_string = f"{clean_date_str} {time_str}".strip()
                try:
                    parsed_dt = parser.parse(full_date_string, fuzzy=True)
                    event_datetime = parsed_dt
                except Exception as e:
                    print(f"Could not parse date '{full_date_string}': {e}")
            
            # Venue
            venue = ""
            venue_tag = event.find(class_='decm_venue')
            if venue_tag:
                venue = venue_tag.text.strip()
            
            # Description (Not provided in the list view, use source name)
            description = "Source: Discover the North Shore"
            
            all_found_events.append({
                "title": title,
                "date_time": event_datetime,
                "venue": venue,
                "url": event_url,
                "description": description
            })
            
        return all_found_events
