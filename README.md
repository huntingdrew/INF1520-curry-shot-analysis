# INF1520-curry-shot-analysis

Final project for INFSCI 1520 (Information Visualization) at the University of Pittsburgh.

This project visualizes Stephen Curry's career shot data across nine NBA regular seasons (2015–16 to 2023–24) using the NBA Stats API. The main figure is a hexagonal frequency map of shot locations, paired with zone-level field goal percentages and a three-point percentage trend across seasons.

## Files

- `curry_shots.py` — fetches data from the NBA Stats API and generates the visualization
- `Figure_1.png` — the main figure used in the report
- `1520 report.pdf` — the final project report

## Usage

Install dependencies:

```
pip install nba_api pandas matplotlib
```

Then run:

```
python curry_shots.py
```

The script will pull shot data from stats.nba.com (takes about a minute) and save the figure as `curry_shot_chart.png`.

## Data Source

NBA Stats API via [nba_api](https://github.com/swar/nba_api)
