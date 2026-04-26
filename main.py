import os
from ics import Calendar, Event
import json

from mkerecord_scraper import MilwaukeeRecordScraper
from mkecounty_scraper import MilwaukeeCountyScraper
from utils import filter_events_with_llm, is_valid_time

def main():
    print("Starting Milwaukee Event Scraper...")
    scrapers = [
        MilwaukeeRecordScraper(),
        MilwaukeeCountyScraper()
    ]
    
    all_events = []
    for scraper in scrapers:
        try:
            events = scraper.scrape()
            print(f"Scraped {len(events)} events from {scraper.__class__.__name__}")
            all_events.extend(events)
        except Exception as e:
            print(f"Error scraping {scraper.__class__.__name__}: {e}")

    print(f"Total raw events: {len(all_events)}")

    # Print out the scraped content for verification
    print("\n--- Extracted Events (Cleaned) ---")
    for ev in all_events:
        # Format the datetime object to a readable string for display
        date_str = ev['date_time'].strftime("%Y-%m-%d %H:%M") if ev.get('date_time') else 'N/A'
        print(f"Title: {ev.get('title')}")
        print(f"Date:  {date_str}")
        print(f"Venue: {ev.get('venue')}")
        print(f"Link:  {ev.get('url')}")
        print(f"Desc:  {ev.get('description', '')[:100]}...\n")

    # Time Filtering
    # We will just print what would be filtered out for debugging right now
    time_filtered_events = []
    for e in all_events:
        if is_valid_time(e['date_time']):
            time_filtered_events.append(e)
            
    print(f"Events matching time filter (Weekend or > 5 PM): {len(time_filtered_events)}")
    
    # LLM Filtering Placeholder
    # Using all_events instead of time_filtered_events right now to ensure we 
    # generate a solid test .ics file regardless of missing time data.
    approved_events = filter_events_with_llm(all_events)
    
    print(f"Events approved by LLM filter: {len(approved_events)}")
    
    if approved_events:
        # Generate ICS Calendar
        cal = Calendar()
        for ev in approved_events:
            c_event = Event()
            c_event.name = ev['title']
            if ev['date_time']:
                c_event.begin = ev['date_time']
            
            # Default duration 2 hours
            c_event.duration = {"hours": 2} 
            
            if ev['venue']:
                c_event.location = ev['venue']
            
            c_event.url = ev['url']
            c_event.description = f"{ev.get('description', '')}\n\nLink: {ev['url']}"
            
            cal.events.add(c_event)
            
        output_file = "mke_events.ics"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(cal.serialize())
            
        print(f"Successfully generated {output_file} with {len(approved_events)} events.")
    else:
        print("No events found to add to calendar.")

if __name__ == "__main__":
    main()