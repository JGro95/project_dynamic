# Cross-border Finance – Interactive Visualization
### Jorge Guerrero
 
 Global borrowing and lending among international banks connect economies and improve capital allocation, promoting investment and larger growth outcomes. However, these linkages also pose risks of crisis that can spill across borders, such as failures to roll over funding or currency shocks. This project builds an interactive web page to explore cross-border banking exposures using Locational Banking Statistics (LBS) collected by the Bank of International Settlements (BIS). The visualizations include funding networks, growth, and concentration to help assess vulnerabilities and inform policy.

You can find the final visualization [here](https://jgro95.github.io/project_dynamic/). 

![](./Cross-Border%20Finance_ss.png)

---

## Project Structure

The page is powered by:

- **Python** (data download & cleaning)
- **D3.js** (Chord diagram)
- **Altair/Vega-Lite** (Charts levels, pct change and HHI)

```text
project_root/
├── main.py                  # Orchestrates the full data pipeline
├── cleaning/
│   ├── get_data.py          # Download & cache raw BIS data
│   ├── chart_1.py           # Build data + spec for 3 charts (levels, changes, hhi)
│   ├── chart_4.py           # Build data for the chord diagram
│   └── concepts/            # ISO codes, GDP
│       ├── countries_iso_codes.csv
│       └── gdp_2024.csv
└── docs/
    ├── index.html           # Main webpage
    ├── data/                # JSON data produced by the pipeline
    ├── js/                  # Front-end JS (D3 functions)
    |── charts/              # Vega/Altair JSON specs
    └── assets/css/          # Styles
```

## Data sources

Data source: [Bank for International Settlements (BIS) – Locational Banking Statistics (LBS).](https://data.bis.org/topics/LBS)

HTML is a modified template from [HTML5 UP](https://html5up.net/)

## Run the project
To run this project run `uv run main.py` and then `uvx livereload www/index.html`



