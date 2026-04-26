import cloudscraper
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
import re

from base_scraper import BaseScraper
from utils import get_next_week_date_range

class MilwaukeeCountyScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://county.milwaukee.gov/EN/News--Events/Events"
        self.scraper = cloudscraper.create_scraper()

    def scrape(self):
        start_date, end_date = get_next_week_date_range()
        all_found_events = []
        
        # We will loop through a few pages of events. 
        # Typically Titan CMS pagination uses a query param like ?PN=1, ?PN=2 or similar.
        # Let's try PN for Page Number, or just fetch the main page if we don't know the param.
        # We can just fetch the first page, and look for "Next" page link.
        
        current_url = self.base_url
        page_count = 0
        current_date_header = None
        
        while current_url and page_count < 5:
            print(f"Fetching Milwaukee County events from: {current_url}")
            try:
                response = self.scraper.get(current_url)
                response.raise_for_status()
            except Exception as e:
                print(f"Failed to fetch events page: {e}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all("div", class_="item")
            
            if not items:
                print("No items found on page.")
                break

            for item in items:
                # Some items have a grouping header for the date
                h3 = item.find("h3", role="presentation")
                if h3:
                    try:
                        current_date_header = parser.parse(h3.text.strip(), fuzzy=True)
                    except Exception:
                        pass
                
                # Title & URL
                title_elem = item.find("a", class_="dataDetailLink")
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                url = title_elem.get("href", "")
                if url.startswith("/"):
                    url = "https://county.milwaukee.gov" + url
                
                # Date & Time from the item details if available, otherwise use header
                date_val = item.find("div", class_="Date")
                time_val = item.find("div", class_="Time")
                
                event_datetime = current_date_header
                
                date_str = ""
                time_str = ""
                if date_val and date_val.find("span", class_="value"):
                    date_str = date_val.find("span", class_="value").text.strip()
                if time_val and time_val.find("span", class_="value"):
                    time_str = time_val.find("span", class_="value").text.strip()
                
                try:
                    if date_str or time_str:
                        d_clean = date_str.split("-")[0].strip() if date_str else ""
                        t_clean = time_str.split("-")[0].strip() if time_str else ""
                        
                        # If date_str is missing, fallback to current_date_header
                        if not d_clean and current_date_header:
                            d_clean = current_date_header.strftime("%Y-%m-%d")
                            
                        # If t_clean is missing, fallback to midnight
                        if not t_clean:
                            t_clean = "00:00"
                            
                        parsed_dt = parser.parse(f"{d_clean} {t_clean}", fuzzy=True)
                        
                        # Ensure year is correct
                        if current_date_header and str(current_date_header.year) not in d_clean:
                            event_datetime = parsed_dt.replace(year=current_date_header.year)
                        else:
                            event_datetime = parsed_dt
                            
                except Exception as e:
                    print(f"Failed to parse date '{date_str}' time '{time_str}' - clean: '{d_clean}' '{t_clean}': {e}")
                    # Keep fallback to current_date_header
                
                # Fallback if no valid date found at all
                if not event_datetime:
                    event_datetime = start_date
                    
                # Venue / Location
                venue = ""
                loc_val = item.find("div", class_=lambda x: x and "Location" in x)
                if loc_val and loc_val.find("span", class_="value"):
                    venue = loc_val.find("span", class_="value").text.strip()
                    
                # Description
                desc = ""
                desc_val = item.find("div", class_="description")
                if desc_val:
                    desc = desc_val.text.strip()
                    
                # Check if it falls within our next week range
                # If the event is past our end_date, we might want to stop, but since we're just
                # collecting for now, let's collect all on the page.
                
                # Deduplicate
                if any(e['title'] == title and e['url'] == url for e in all_found_events):
                    continue
                    
                all_found_events.append({
                    "title": title,
                    "date_time": event_datetime,
                    "venue": venue,
                    "url": url,
                    "description": f"Source: Milwaukee County\n{desc[:300]}..."
                })
            
            # Find next page link
            next_link = soup.find("a", class_="next")
            if next_link and next_link.get("href"):
                next_url = next_link["href"]
                if next_url.startswith("/"):
                    current_url = "https://county.milwaukee.gov" + next_url
                else:
                    current_url = next_url
            else:
                # Look for pagination via query params
                pagination = soup.find("div", class_="pagination")
                if pagination:
                    next_page_elem = pagination.find("a", string=re.compile(r"Next|&gt;|»"))
                    if next_page_elem and next_page_elem.get("href"):
                        current_url = "https://county.milwaukee.gov" + next_page_elem["href"] if next_page_elem["href"].startswith("/") else next_page_elem["href"]
                    else:
                        current_url = None
                else:
                    current_url = None
                
            page_count += 1
            
        return all_found_events
