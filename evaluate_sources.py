import os
import json
from collections import defaultdict
from orchestrator import get_city_config, load_scrapers

def evaluate_event(event):
    # Heuristics based on user preferences
    # 1. Strongly prefer "DO"
    # 2. No interest in passive "SEE"
    # 3. LOVE hands-on, unique, participatory
    # 4. Like outdoor activities and athletic events
    
    text = (event.get('title', '') + " " + event.get('description', '')).lower()
    
    positive_keywords = [
        'workshop', 'class', 'make', 'create', 'paint', 'craft', 'carve',
        'run', 'bike', 'hike', 'athletic', 'sport', 'tournament', 'outdoor',
        'hands-on', 'interactive', 'participate', 'volunteer', 'yoga', 'fitness',
        'build', 'tour', 'walk', 'race', 'climb'
    ]
    
    negative_keywords = [
        'concert', 'music', 'band', 'orchestra', 'symphony',
        'gallery', 'exhibit', 'museum', 'viewing', 'art show',
        'play', 'theatre', 'theater', 'musical', 'performance', 'show',
        'lecture', 'talk', 'presentation', 'author', 'reading'
    ]
    
    score = 0
    for pk in positive_keywords:
        if pk in text:
            score += 2
            
    for nk in negative_keywords:
        if nk in text:
            score -= 2
            
    # Normalize score somewhat
    if score >= 2:
        return "Good"
    elif score < 0:
        return "Bad"
    else:
        return "Neutral"

def main():
    config_path = os.path.join(os.path.dirname(__file__), "cities.json")
    city_config = get_city_config(config_path, "mke")
    scrapers = load_scrapers(city_config)
    
    source_stats = defaultdict(lambda: {"total": 0, "good": 0, "neutral": 0, "bad": 0})
    
    for scraper in scrapers:
        source_name = scraper.__class__.__name__
        try:
            print(f"Scraping from {source_name}...")
            events = scraper.scrape()
            for ev in events:
                eval_res = evaluate_event(ev)
                source_stats[source_name]["total"] += 1
                if eval_res == "Good":
                    source_stats[source_name]["good"] += 1
                elif eval_res == "Neutral":
                    source_stats[source_name]["neutral"] += 1
                elif eval_res == "Bad":
                    source_stats[source_name]["bad"] += 1
        except Exception as e:
            print(f"Error scraping {source_name}: {e}")

    print("\n--- Evaluation Results ---")
    total_good = sum(stats["good"] for stats in source_stats.values())
    total_events = sum(stats["total"] for stats in source_stats.values())
    
    if total_events == 0:
        print("No events found.")
        return
        
    for source, stats in source_stats.items():
        if stats["total"] == 0:
            continue
        good_pct = (stats["good"] / stats["total"]) * 100
        bad_pct = (stats["bad"] / stats["total"]) * 100
        overall_good_pct = (stats["good"] / max(1, total_good)) * 100
        
        print(f"\nSource: {source}")
        print(f"  Total Events: {stats['total']}")
        print(f"  Good (Match): {stats['good']} ({good_pct:.1f}%)")
        print(f"  Bad (Passive): {stats['bad']} ({bad_pct:.1f}%)")
        print(f"  % of Total Good Events: {overall_good_pct:.1f}%")

if __name__ == "__main__":
    main()
