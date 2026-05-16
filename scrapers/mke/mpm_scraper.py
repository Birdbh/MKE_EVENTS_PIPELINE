import cloudscraper
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
import os
import sys

# Ensure we can import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from base_scraper import BaseScraper
from utils import get_next_week_date_range

class MPMScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://milwaukeepublicmarket.org/event/upcoming-events"
        self.domain = "https://milwaukeepublicmarket.org"
        self.scraper = cloudscraper.create_scraper()

    def scrape(self):
        start_date, end_date = get_next_week_date_range()
        all_found_events = []
        
        print(f"Fetching Milwaukee Public Market events from: {self.base_url}")
        try:
            response = self.scraper.get(self.base_url)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch MPM events page: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        # Find all event links
        events = soup.find_all('a', class_='upcomingevents_linkblock')
        
        for event in events:
            # URL
            href = event.get('href', '')
            if href.startswith('/'):
                event_url = self.domain + href
            else:
                event_url = href
                
            # Title
            title_tag = event.find(class_='vendor-listing-name')
            if not title_tag:
                continue
            title = title_tag.text.strip()
            
            # Deduplicate
            if any(e['title'] == title and e['url'] == event_url for e in all_found_events):
                continue
                
            # Date
            date_tags = event.find_all(class_='event-dat')
            date_str = ""
            if date_tags:
                date_str = date_tags[0].text.strip()
                
            # Time
            time_tag = event.find(class_='event-time')
            time_str = ""
            if time_tag:
                time_str = time_tag.text.strip()
                
            # Combine Date and Time
            full_date_str = f"{date_str} {time_str}".strip()
            event_datetime = start_date # default
            if full_date_str:
                try:
                    parsed_dt = parser.parse(full_date_str, fuzzy=True)
                    event_datetime = parsed_dt
                except Exception as e:
                    print(f"Could not parse date '{full_date_str}': {e}")
            
            # Venue
            venue = "Milwaukee Public Market, 400 N. Water Street, Milwaukee, WI 53202"
            
            # Description
            description = "Source: Milwaukee Public Market"
            
            all_found_events.append({
                "title": title,
                "date_time": event_datetime,
                "venue": venue,
                "url": event_url,
                "description": description
            })
            
        return all_found_events
