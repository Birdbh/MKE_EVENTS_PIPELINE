---
name: create-scraper
description: Autonomously creates and registers a new event scraper for a specific city. Use when the user wants to add a new event source, mentions "new scraper", or provides a URL and city to scrape events from.
---

# Create Scraper

## Quick start

User says: "Create a scraper for Chicago using this URL: https://example.com/events"
You use this skill to autonomously write and register the scraper.

## Workflow

When invoked with a **URL** and a **Target City Code** (e.g., 'mke', 'chi'), follow these steps fully autonomously:

1. **Analyze Source**:
   - Use `read_url_content` or a Python script to fetch the HTML from the provided URL.
   - Identify the structure of the events list (title, date/time, venue, description, link).

2. **Generate Scraper**:
   - Write a new Python class that inherits from `BaseScraper` (located in `mke_events/base_scraper.py`).
   - Implement the `scrape()` method to extract events from the HTML.
   - The `scrape()` method MUST return a list of dictionaries with keys: `title`, `date_time` (datetime object), `venue`, `url`, `description`.

3. **Save Scraper**:
   - Create the directory `mke_events/scrapers/<city>/` if it does not exist, and ensure it has an `__init__.py` file.
   - Save the new scraper as `mke_events/scrapers/<city>/<source_name>_scraper.py`.

4. **Register Scraper**:
   - Open `mke_events/cities.json`.
   - Add the new scraper's module path (e.g., `"scrapers.<city>.<source_name>_scraper.<ClassName>"`) to the `scrapers` list under the correct city key. If the city key does not exist, initialize it.

5. **Test Scraper**:
   - Run a quick python command to instantiate and test the scraper to ensure it returns events. Provide the user with the number of events found.
