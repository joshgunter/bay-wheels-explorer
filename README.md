# Bay Wheels Explorer

Interactive dashboard analyzing 21.5M+ Bay Wheels bike-share trips across the San Francisco Bay Area (Jun 2017 – Jan 2026).

**[View Live Dashboard](https://joshgunter.github.io/bay-wheels-explorer/)**

## Features

- **Overview** — Yearly growth, bike type breakdown, monthly volume, key insights
- **Station Map** — Interactive map of all 835 stations with filtering
- **Station Rankings** — Sortable table of all stations by performance metrics
- **Top Routes** — 100 most popular origin-destination routes
- **Time Patterns** — Hourly and day-of-week usage analysis

## Data Source

Lyft Bay Wheels open data: https://www.lyft.com/bikes/bay-wheels/system-data

## Updating the Data

1. Download new monthly CSV/ZIP files from the Lyft Bay Wheels system data page
2. Place them in a `data/` folder
3. Run: `python scripts/preprocess.py --data-dir ./data/`
4. Run: `python scripts/build_dashboard.py`
5. Commit and push the updated `index.html`
