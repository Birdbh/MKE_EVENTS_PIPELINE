import cloudscraper
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
import re
import os
import sys

# Ensure we can import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from base_scraper import BaseScraper
from utils import get_next_week_date_range

class UrbanMilwaukeeScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://urbanmilwaukee.com/events/"
        self.scraper = cloudscraper.create_scraper()

    def scrape(self):
        start_date, end_date = get_next_week_date_range()
        date_str = start_date.strftime("%Y-%m-%d")
        
        all_found_events = []
        page = 1
        
        while page <= 5: # Max 5 pages to be safe
            url = f"{self.base_url}?tribe_paged={page}&tribe_event_display=list&tribe-bar-date={date_str}"
            print(f"Fetching Urban Milwaukee events from: {url}")
            
            try:
                response = self.scraper.get(url)
                response.raise_for_status()
            except Exception as e:
                print(f"Failed to fetch Urban Milwaukee events page {page}: {e}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            events = soup.find_all('div', class_=lambda x: x and 'type-tribe_events' in x)
            
            if not events:
                print("No more events found on this page.")
                break
                
            for event in events:
                title_tag = event.find('h2', class_='tribe-events-list-event-title')
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
                date_tag = event.find('span', class_='tribe-event-date-start')
                event_datetime = start_date # default
                if date_tag:
                    date_text = date_tag.text.strip()
                    # e.g., "May 20 @ 7:30 pm"
                    # We might need to add the year from start_date
                    date_text_clean = date_text.replace('@', '').strip()
                    try:
                        parsed_dt = parser.parse(date_text_clean, fuzzy=True)
                        # The parser might use current year, let's explicitly set it if we cross years, but usually it's fine
                        # Let's ensure year is at least start_date's year
                        # Because fuzzy parser might assume current year (e.g. 2026), which is correct.
                        event_datetime = parsed_dt.replace(year=start_date.year)
                        
                        # Sometimes date_text_clean doesn't have time, it just says "May 20"
                        # If the time is 00:00:00, let's check if there's an end time or something, but 00:00:00 is fine.
                    except Exception as e:
                        print(f"Could not parse date '{date_text}': {e}")
                        
                # If event is completely outside our range, we might skip it, but let's just collect it and let limit_events handle
                
                # Venue
                venue = ""
                venue_tag = event.find('div', class_='tribe-events-venue-details')
                if venue_tag:
                    # Remove the Google Map link
                    gmap = venue_tag.find('a', class_='tribe-events-gmap')
                    if gmap:
                        gmap.extract()
                    venue = venue_tag.text.strip()
                    venue = re.sub(r'\s+', ' ', venue).strip() # Clean up whitespace
                    # Remove trailing comma
                    if venue.endswith(','):
                        venue = venue[:-1]
                
                # Description
                description = ""
                desc_tag = event.find('div', class_='tribe-events-list-event-description')
                if desc_tag:
                    p_tag = desc_tag.find('p')
                    if p_tag:
                        description = p_tag.text.strip()
                        
                all_found_events.append({
                    "title": title,
                    "date_time": event_datetime,
                    "venue": venue,
                    "url": event_url,
                    "description": f"Source: Urban Milwaukee\n{description[:300]}..."
                })
                
            # Check if there's a next page link
            next_link = soup.find('li', class_='tribe-events-nav-next')
            if not next_link or not next_link.find('a'):
                break
                
            page += 1
            
        return all_found_events
