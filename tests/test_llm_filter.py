import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import parse_and_sort_llm_response

def test_parse_and_sort_llm_response():
    events = [
        {"title": "Event 0"},
        {"title": "Event 1"},
        {"title": "Event 2"},
        {"title": "Event 3"}
    ]
    
    # LLM returned scores for events 1, 3, 0 in that order
    # Notice it skipped event 2
    llm_json = '''
    [
        {"id": 3, "score": 9},
        {"id": 1, "score": 5},
        {"id": 0, "score": 10}
    ]
    '''
    
    sorted_events = parse_and_sort_llm_response(events, llm_json)
    
    assert len(sorted_events) == 3
    # Should be sorted descending by score: 0 (score 10), 3 (score 9), 1 (score 5)
    assert sorted_events[0]["title"] == "Event 0"
    assert sorted_events[1]["title"] == "Event 3"
    assert sorted_events[2]["title"] == "Event 1"

def test_parse_and_sort_llm_response_invalid_json():
    events = [{"title": "Event 0"}]
    # If LLM returns garbage, return the original list
    sorted_events = parse_and_sort_llm_response(events, "invalid json")
    assert len(sorted_events) == 1
    assert sorted_events[0]["title"] == "Event 0"
