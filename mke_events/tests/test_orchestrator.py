import pytest
import sys
import os

# Add parent dir to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator import load_scrapers

def test_load_scrapers_dynamically():
    config = {
        "scrapers": [
            "scrapers.mke.mkecounty_scraper.MilwaukeeCountyScraper"
        ]
    }
    
    # Act
    scrapers = load_scrapers(config)
    
    # Assert
    assert len(scrapers) == 1
    assert scrapers[0].__class__.__name__ == "MilwaukeeCountyScraper"
    assert hasattr(scrapers[0], 'scrape')
