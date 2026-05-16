import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import limit_events_per_day

def test_limit_events_per_day():
    # Construct a list of dummy events
    # Monday = weekday = max 2
    # Saturday = weekend = max 5
    monday_dt = datetime(2026, 5, 18, 12, 0)
    saturday_dt = datetime(2026, 5, 23, 12, 0)
    
    events = []
    # 4 events on Monday
    for i in range(4):
        events.append({"title": f"Monday {i}", "date_time": monday_dt, "score": 10-i})
        
    # 10 events on Saturday
    for i in range(10):
        events.append({"title": f"Saturday {i}", "date_time": saturday_dt, "score": 10-i})
        
    # They should already be sorted by score from the LLM parsing
    final_events = limit_events_per_day(events)
    
    mon_count = sum(1 for e in final_events if e['date_time'] == monday_dt)
    sat_count = sum(1 for e in final_events if e['date_time'] == saturday_dt)
    
    assert mon_count == 2
    assert sat_count == 5
    
    # Check that it kept the highest scored ones (0 and 1 for Monday)
    mon_titles = [e['title'] for e in final_events if e['date_time'] == monday_dt]
    assert "Monday 0" in mon_titles
    assert "Monday 1" in mon_titles
