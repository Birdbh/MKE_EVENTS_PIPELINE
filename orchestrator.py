import importlib
import json

def get_city_config(config_path, city_name):
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if city_name not in data:
        raise ValueError(f"City '{city_name}' not found in config")
        
    return data[city_name]

def load_scrapers(config):
    scrapers = []
    for scraper_path in config.get("scrapers", []):
        # Split module path and class name
        # e.g., "mkerecord_scraper.MilwaukeeRecordScraper"
        parts = scraper_path.split('.')
        module_name = '.'.join(parts[:-1])
        class_name = parts[-1]
        
        module = importlib.import_module(module_name)
        scraper_class = getattr(module, class_name)
        scrapers.append(scraper_class())
        
    return scrapers
