# Cross-border Finance – Interactive Visualization

This project builds an interactive web page to explore cross-border banking exposures using BIS Locational Banking Statistics (LBS).  
The page is powered by:

- **Python** (data download & cleaning)
- **Altair/Vega-Lite** (Charts 1 & 2)
- **D3.js** (Chord diagram for Chart 3)

---

## Project Structure

```text
project_root/
├── main.py                  # Orchestrates the full data pipeline
├── cleaning/
│   ├── get_data.py          # Download & cache raw BIS data
│   ├── chart_1.py           # Build data + spec for Chart 1
│   ├── chart_2.py           # Build data + spec for Chart 2
│   ├── chart_4.py           # Build data for the chord diagram
│   └── concepts/            # ISO codes, GDP, etc.
│       ├── countries_iso_codes.csv
│       └── gdp_2024.csv
└── www/
    ├── index.html           # Main webpage
    ├── css/                 # Styles
    ├── js/                  # Front-end JS (D3 functions)
    ├── data/                # JSON data produced by the pipeline
    └── charts/              # Vega/Altair JSON specs

```
## Run

To run this project run `uv run main.py` and then `uvx livereload www/index.html`



