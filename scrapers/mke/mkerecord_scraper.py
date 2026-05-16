import cloudscraper
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
import re

from base_scraper import BaseScraper
from utils import get_next_week_date_range

class MilwaukeeRecordScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://milwaukeerecord.com/category/music/"
        # We need cloudscraper to bypass Cloudflare
        self.scraper = cloudscraper.create_scraper()

    def get_latest_events_url(self):
        response = self.scraper.get(self.base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all links on the music page
        links = []
        for a in soup.find_all('a', href=True):
            if 'recommended-events' in a['href']:
                links.append(a['href'])
                
        # Return the first unique link
        if links:
            return list(dict.fromkeys(links))[0] # preserve order but remove duplicates
        return None

    def scrape(self):
        start_date, end_date = get_next_week_date_range()
        all_found_events = []
        
        events_url = self.get_latest_events_url()
        if not events_url:
            print("Could not find the latest Milwaukee Record Recommended Events article.")
            return []
            
        print(f"Fetching Milwaukee Record events from: {events_url}")
        
        try:
            response = self.scraper.get(events_url)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch events article: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        
        # The content wrapper is section.cb-entry-content
        content = soup.find("section", class_="cb-entry-content")
        if not content:
            print("Could not find the article content container.")
            return []
            
        current_date = None
        
        # Iterate through all children of the content container
        for element in content.children:
            if element.name == 'h1':
                # Check if it's a date header like MONDAY, APRIL 20
                header_text = element.text.strip()
                if header_text and any(day in header_text.upper() for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]):
                    try:
                        # Append the current year to the parsed date text
                        year = datetime.now().year
                        current_date = parser.parse(f"{header_text}, {year}")
                    except Exception as e:
                        print(f"Could not parse header date '{header_text}': {e}")
                        current_date = None
            
            elif element.name == 'p' and current_date:
                # This is potentially an event description
                # Typically formatted as <strong><a href="...">Title @ Venue</a></strong><br/>Description
                
                strong_tag = element.find('strong')
                if not strong_tag:
                    continue
                    
                full_title_venue = strong_tag.text.strip()
                if not full_title_venue or "@" not in full_title_venue:
                    continue
                    
                # Split Title and Venue
                parts = full_title_venue.split("@", 1)
                title = parts[0].strip()
                venue = parts[1].strip() if len(parts) > 1 else ""
                
                # Check for link
                link_tag = strong_tag.find('a', href=True)
                url = link_tag['href'] if link_tag else events_url
                
                # Extract description (everything after the <br/> or the strong tag)
                # An easy way is to get all text from the p tag and remove the title/venue part
                full_text = element.text.strip()
                description = full_text.replace(full_title_venue, "", 1).strip()
                
                # Filter strictly for events in the next week based on parsed date
                # Actually, the user wants the events from the article, which usually covers the current week.
                # Let's include all of them and let the time_filtered_events log them or we just return them all.
                all_found_events.append({
                    "title": title,
                    "date_time": current_date,
                    "venue": venue,
                    "url": url,
                    "description": f"Source: Milwaukee Record\n{description[:300]}..."
                })

        return all_found_events
