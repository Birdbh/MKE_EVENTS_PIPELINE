from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def scrape(self):
        """
        Must return a list of dictionaries representing events.
        Expected format:
        {
            'title': 'Event Title',
            'date_time': datetime_object,
            'venue': 'Venue Name',
            'url': 'Event Link (or source page)',
            'description': 'Optional description'
        }
        """
        pass