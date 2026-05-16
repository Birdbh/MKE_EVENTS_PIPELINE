import os
import json
from datetime import datetime, timedelta

def get_next_week_date_range():
    """Returns the start and end dates for the upcoming 7 days."""
    today = datetime.now()
    
    # Set times to start of today and end of today + 7 days
    start_time = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_date = today + timedelta(days=7)
    end_time = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
    
    return start_time, end_time

def is_valid_time(event_datetime):
    """
    Checks if the event is happening on a weekend or after 5 PM.
    """
    if event_datetime is None:
        return False
    
    is_weekend = event_datetime.weekday() >= 5
    is_after_five = event_datetime.hour >= 17
    
    return is_weekend or is_after_five

from collections import defaultdict

def limit_events_per_day(events):
    """
    Limits the number of events per day.
    Assumes events are already sorted by score (highest first).
    Max 2 on weekdays, Max 5 on weekends.
    """
    final_events = []
    events_by_date = defaultdict(list)
    for ev in events:
        dt = ev['date_time']
        date_key = dt.date()
        events_by_date[date_key].append(ev)
        
    for date_key in sorted(events_by_date.keys()):
        day_events = events_by_date[date_key]
        # Weekday (0-4 is Mon-Fri)
        if date_key.weekday() < 5:
            selected = day_events[:2]
        else:
            selected = day_events[:5]
        final_events.extend(selected)
        
    return final_events

def parse_and_sort_llm_response(events, llm_json_text):
    """
    Parses the JSON response from the LLM, which should be a list of dicts:
    [{"id": int, "score": int}]
    Returns the events sorted by score descending.
    """
    try:
        parsed_data = json.loads(llm_json_text)
        if not isinstance(parsed_data, list):
            print("WARNING: LLM did not return a list. Returning all events.")
            return events
            
        scored_events = []
        for item in parsed_data:
            if isinstance(item, dict) and 'id' in item and 'score' in item:
                event_id = item['id']
                if 0 <= event_id < len(events):
                    event_copy = events[event_id].copy()
                    event_copy['score'] = item['score']
                    scored_events.append(event_copy)
            elif isinstance(item, int): # Fallback for old list of ints
                if 0 <= item < len(events):
                    scored_events.append(events[item])
                    
        # Sort by score descending (if score exists, otherwise fallback to 0)
        scored_events.sort(key=lambda x: x.get('score', 0), reverse=True)
        return scored_events
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return events

def filter_events_with_llm(events):
    """
    Uses the Gemini API to filter events based on user preferences.
    """
    if not events:
        return []
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY environment variable not set. Skipping LLM filtering and returning all events.")
        return events

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("WARNING: google-genai library not installed. Skipping LLM filtering.")
        return events

    print(f"\nSending {len(events)} events to Gemini for filtering and scoring based on preferences...")
    client = genai.Client(api_key=api_key)

    # Prepare events list for the prompt
    events_text = ""
    for i, ev in enumerate(events):
        date_str = ev['date_time'].strftime("%Y-%m-%d %H:%M") if ev.get('date_time') else 'Unknown'
        # Clean up description to save tokens
        desc = ev.get('description', '')[:250].replace('\n', ' ')
        events_text += f"ID: {i} | Title: {ev['title']} | Date: {date_str} | Venue: {ev['venue']} | Desc: {desc}...\n"

    prompt = f"""You are an intelligent event curation assistant. Your job is to filter and score a list of upcoming events based strictly on my preferences.

My Preferences:
1. I strongly prefer "DO" events over "SEE" events. 
2. I have NO interest in passive events where I am just looking or listening (e.g., viewing an art gallery, looking at paintings, watching a standard concert or play).
3. I LOVE hands-on, unique, participatory activities (e.g., painting, carving, crafting, or any special unique art situation where I am actively creating or participating).
4. I like outdoor activities and athletic events a lot.

Below is a list of events. Please evaluate each event against my preferences. 

Return ONLY a valid JSON array of objects for the events that match my preferences. 
Each object must have exactly two keys: "id" (the integer ID of the event) and "score" (an integer from 1 to 10 indicating how strongly it matches my preferences, with 10 being a perfect match).
Do not include any markdown formatting, explanations, or other text. If no events match, return an empty array `[]`.

Events:
{events_text}
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        return parse_and_sort_llm_response(events, response.text)
        
    except Exception as e:
        print(f"Error during LLM filtering: {e}")
        return events