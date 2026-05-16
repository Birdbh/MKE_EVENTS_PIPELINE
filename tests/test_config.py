import pytest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator import get_city_config

def test_get_city_config(tmp_path):
    config_file = tmp_path / "cities.json"
    config_data = {
        "mke": {
            "scrapers": [
                "scrapers.mke.mkerecord_scraper.MilwaukeeRecordScraper"
            ]
        }
    }
    config_file.write_text(json.dumps(config_data))
    
    config = get_city_config(str(config_file), "mke")
    assert "scrapers" in config
    assert len(config["scrapers"]) == 1
    assert config["scrapers"][0] == "scrapers.mke.mkerecord_scraper.MilwaukeeRecordScraper"

def test_get_city_config_not_found(tmp_path):
    config_file = tmp_path / "cities.json"
    config_file.write_text(json.dumps({}))
    
    with pytest.raises(ValueError, match="City 'chi' not found in config"):
        get_city_config(str(config_file), "chi")
