#Milwaukee Events Pipeline 📊

A comprehensive data pipeline that aggregates, cleans, and analyzes event listings from Milwaukee's major ticketing platforms. This project transforms raw event data into structured insights, enabling data-driven decisions for event organizers and enthusiasts.

## Features

- **Multi-Source Ingestion** - Collects event data from:
  - **Eventbrite** - Local and global events, including venue, date, and ticket price data
  - **Ticketmaster** - Major concerts, sports, and entertainment events
  - **Live Nation** - Festival and venue-specific event listings
  - **The Rave** - Milwaukee's premier music venue events
- **Data Processing Pipeline** - Automated ETL (Extract, Transform, Load) workflow:
  - **Data Cleaning** - Standardizes event details, removes duplicates, and ensures data quality
  - **Schema Normalization** - Converts diverse data formats into a unified structure
  - **Geo-tagging** - Assigns latitude/longitude coordinates to event venues
- **Interactive Visualization** - Comprehensive analytics dashboard using Streamlit:
  - **Geospatial Mapping** - Visualizes event density across Milwaukee with clustering
  - **Time-Series Analysis** - Tracks event trends by day, week, and month
  - **Category Analysis** - Identifies popular genres and event types
  - **Venue Insights** - Ranks top venues by event volume and popularity
- **Database Integration** - Stores processed data in a SQLite database for easy querying

## Tech Stack

### Backend
- **Python 3.11+** - Core programming language
- **FastAPI** - Web framework for API endpoints
- **SQLAlchemy** - Database ORM for SQLite
- **Pandas** - Data manipulation and analysis
- **Requests** - HTTP client for API requests
- **Google Maps API** - Geocoding and location services

### Frontend & Analytics
- **Streamlit** - Interactive web application framework
- **Plotly Express** - Data visualization library
- **Folium** - Interactive mapping library

### Infrastructure
- **Docker** - Containerization for consistent environments
- **Docker Compose** - Multi-container orchestration

## Project Structure

```
mke-events-pipeline/
├── src/
│   ├── api/                  # FastAPI backend endpoints
│   ├── services/             # Data collection services
│   ├── utils/                # Utility functions (geocoding, DB)
│   ├── visualization/        # Streamlit dashboard components
│   ├── pipelines/            # ETL pipeline orchestrators
│   └── models/               # Database models
├── data/                     # Raw and processed data
├── notebooks/                # Jupyter notebooks for analysis
└── deployment/               # Docker configuration
```

## Installation

### Prerequisites
- Python 3.11 or higher
- Docker and Docker Compose (optional)

### Option 1: Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/birdlaw7/mke-events-pipeline.git
   cd mke-events-pipeline
   ```

2. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your API keys and configuration:
   ```env
   GOOGLE_MAPS_API_KEY=your_api_key_here
   EVENTBRITE_API_KEY=your_eventbrite_key
   ```

4. Build and run the application:
   ```bash
   docker-compose up --build
   ```

### Option 2: Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/birdlaw7/mke-events-pipeline.git
   cd mke-events-pipeline
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```env
   GOOGLE_MAPS_API_KEY=your_api_key_here
   EVENTBRITE_API_KEY=your_eventbrite_key
   ```

5. Run the database migrations:
   ```bash
   python src/models/database.py init
   ```

## Usage

### Start the FastAPI Server
```bash
uvicorn src.api.main:app --reload
```
Access the interactive API docs at `http://localhost:8000/docs`

### Run the Streamlit Dashboard
```bash
streamlit run src/visualization/app.py
```
The dashboard will open automatically in your browser

### Execute Data Collection Scripts
```bash
python src/pipelines/eventbrite_pipeline.py
python src/pipelines/ticketmaster_pipeline.py
python src/pipelines/liver_pipeline.py
```
Each script collects data from its respective platform and updates the database

## Data Collection Strategies

### Eventbrite
- Uses `requests` with API authentication to fetch events
- Fetches events for Milwaukee and Surrounding Areas (2019-2028)
- Retrieves detailed event information including category, venue, and pricing

### Ticketmaster
- Employs pagination to retrieve large datasets
- Fetches events from 2024-2027 for the Milwaukee area
- Collects event metadata including classification and sales status

### Live Nation
- Scrapes Live Nation website for festivals and concerts
- Extracts event names, dates, and venue locations
- Identifies festival events with multi-day information

### The Rave
- Collects upcoming events from The Rave's website
- Retrieves event titles, dates, and genres
- Supports venue-specific analytics and insights

## Data Model

The database schema includes:
- `events`: Master event table with normalized details
- `event_metadata`: Category, genre, and status information
- `venues`: Venue details with geocoding
- `collection_logs`: Pipeline execution tracking

## API Endpoints

- `GET /events`: Retrieve all events with optional filtering
- `GET /events/{id}`: Get specific event details
- `GET /events/date/{date}`: Events for a specific date
- `GET /events/categories`: List available event categories
- `GET /events/count`: Event statistics by category
- `GET /events/popular`: Most popular events by views

## Analysis Capabilities

### Geospatial Analysis
- **Heatmaps**: Visualize event hotspots across Milwaukee
- **Clustering**: Identify dense event clusters using HDBSCAN
- **Venue Density**: Map venue distribution by capacity

### Time-Series Analysis
- **Weekly Trends**: Track event volume by day of the week
- **Monthly Analysis**: Monitor event trends over time
- **Year-over-Year**: Compare event volumes across years
- **Seasonality**: Identify peak seasons for different genres

### Categorical Analysis
- **Genre Breakdown**: Distribution of event categories
- **Top Genres**: Identify most popular event types
- **Niche Markets**: Track emerging genres and trends

### Venue Analytics
- **Top Venues**: Rank venues by event count
- **Capacity Analysis**: Match venue capacity to event demand
- **Attendance Estimation**: Predict attendance based on venue size

## Development

To add a new data source:
1. Create a new collection service in `src/services/`
2. Add a pipeline orchestrator in `src/pipelines/`
3. Update `src/api/main.py` to register the new endpoint
4. Add database models in `src/models/`
5. Update `deployment/docker-compose.yml` if needed

## Local Testing

Run the database tests:
```bash
python -m unittest tests/test_database.py
```

Run API tests:
```bash
python -m unittest tests/test_api.py
```

## License

This project is for educational purposes and data analysis experimentation. The code is provided under the MIT License. API usage is subject to the terms of service of each respective platform.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

##
