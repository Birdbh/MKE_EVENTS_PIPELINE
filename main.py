import os
import hashlib
from zoneinfo import ZoneInfo
from ics import Calendar, Event

from orchestrator import get_city_config, load_scrapers
from utils import filter_events_with_llm, limit_events_per_day, is_valid_time, get_next_week_date_range

def main():
    print("Starting Multi-City Event Scraper...")
    # Read the city from environment variable or default to 'mke'
    city = os.environ.get("TARGET_CITY", "mke")
    print(f"Targeting city: {city}")
    
    config_path = os.path.join(os.path.dirname(__file__), "cities.json")
    try:
        city_config = get_city_config(config_path, city)
    except Exception as e:
        print(f"Error loading config for {city}: {e}")
        return

    scrapers = load_scrapers(city_config)
    
    all_events = []
    for scraper in scrapers:
        try:
            events = scraper.scrape()
            print(f"Scraped {len(events)} events from {scraper.__class__.__name__}")
            all_events.extend(events)
        except Exception as e:
            print(f"Error scraping {scraper.__class__.__name__}: {e}")

    print(f"Total raw events: {len(all_events)}")
    
    start_date, end_date = get_next_week_date_range()
    print(f"Targeting events strictly between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")

    base_filtered_events = []
    for ev in all_events:
        dt = ev.get('date_time')
        
        # 1. Strict Date Range Filter
        if not dt or not (start_date.date() <= dt.date() <= end_date.date()):
            continue
            
        # 2. Filter out Virtual / Online events
        title_lower = ev.get('title', '').lower()
        venue_lower = ev.get('venue', '').lower()
        if "virtual" in venue_lower or "online" in venue_lower or "virtual" in title_lower or "online" in title_lower:
            continue
            
        base_filtered_events.append(ev)
        
    print(f"Events remaining after date & offline filters: {len(base_filtered_events)}")

    # Time Filtering (Optional debugging info)
    time_filtered_events = []
    for e in base_filtered_events:
        if is_valid_time(e['date_time']):
            time_filtered_events.append(e)
            
    print(f"Events matching time filter (Weekend or > 5 PM): {len(time_filtered_events)}")
    
    # 3. LLM Filtering and Scoring
    scored_events = filter_events_with_llm(base_filtered_events)
    print(f"Events approved by LLM filter: {len(scored_events)}")
    
    # 4. Limit events based on day of week
    final_events = limit_events_per_day(scored_events)
    print(f"Final events after weekday/weekend limits applied: {len(final_events)}")

    # Generate ICS Calendar
    if final_events:
        cal = Calendar()
        cst_zone = ZoneInfo("America/Chicago")
        
        for ev in final_events:
            c_event = Event()
            c_event.name = ev['title']
            
            # Deterministic UID based on title and date so calendars don't duplicate events if the script runs twice
            uid_string = f"{ev['title']}-{ev['date_time']}".encode('utf-8')
            c_event.uid = hashlib.md5(uid_string).hexdigest() + f"@{city}_events.local"
            
            dt = ev['date_time']
            
            # If the event starts exactly at midnight, let's treat it as an all day event 
            # to avoid 7 PM off-by-1 timezone bugs when loading into Google Calendar.
            if dt.hour == 0 and dt.minute == 0:
                c_event.begin = dt.date()
                c_event.make_all_day()
            else:
                # Make the datetime timezone aware if it is naive
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=cst_zone)
                c_event.begin = dt
                c_event.duration = {"hours": 2} 
            
            if ev['venue']:
                c_event.location = ev['venue']
            
            c_event.url = ev['url']
            c_event.description = f"{ev.get('description', '')}\n\nLink: {ev['url']}"
            
            cal.events.add(c_event)
            
        output_file = f"{city}_events.ics"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(cal.serialize())
            
        print(f"Successfully generated {output_file} with {len(final_events)} events.")
    else:
        print("No events found to add to calendar.")

if __name__ == "__main__":
    main()