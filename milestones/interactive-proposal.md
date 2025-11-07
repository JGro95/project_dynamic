# Jorge Guerrero - Cross border finance

## Description

This project will explore how **international lending and borrowing patterns**, using data from the Bank for International Settlements’ Locational Banking Statistics (LBS).

The visualization will allow users to interactively examine how financial connections between countries have evolved, who the main lenders and borrowers are, and how financial exposure varies by region or income group.

The goal is to make complex global finance network data more readable/easy to explore by emphasizing trends, asymmetries, and interdependence in the international financial system.

---

## Technical Plan: Option B - Dynamic Ensemble

Instead of a single chart, the project will present a **Dynamic Ensemble** — a cohesive set of interactive visualizations that together tell a story of how money flows across borders. Users will be able to:

- Filter and compare countries or regions.
- Observe the evolution of claims and liabilities over time.
- Explore the global lending network from different perspectives (by country, instrument, currency).
- Use a simulation of defaults and its propagation through the network.[may be]


### Tools and Framework

- Altair (Python) for creating interactive Vega-Lite visualizations.
- Basic HTML + CSS layout to unify the style, typography, and narrative text.

### Inspiration
#### Related to the topic:
 - BIS website offers an interactive dashboard to explore the data of the Locational Banking statistics, available: https://data.bis.org/topics/LBS/tables-and-dashboards


#### Network visualization: 
 - A Day in the Life of Americans, available: https://flowingdata.com/2015/12/15/a-day-in-the-life-of-americans/
 - https://www.data-to-viz.com/story/AdjacencyMatrix.html
 - https://dash.gallery/retail-demand-transference/?_gl=1*13q3d00*_gcl_au*ODQ5Mzk0MDg2LjE3NjA2NDU4OTI.*_ga*MTU1NDkxNDA2OS4xNzYwNjQ1ODkz*_ga_6G7EE0JNSC*czE3NjI1MzA1NTQkbzMkZzEkdDE3NjI1MzA2MzQkajYwJGwwJGgw
 


---

## Mockup

### Visualizations Planned

1. **Global Financial Growth Overview**
   - Interactive line and area chart showing total claims, liabilities, and net positions since 2000.
   - Dropdown to select specific regions (e.g., Americas, Europe, Asia) or country, instrument.

2. **Regional and Income-Group Comparison**
   - Interactive stacked area or bar chart showing exposures by income group.
   - Slider or year-selection dropdown to view different periods (2000–2024).

3. **Country-Level Balance Explorer (Scatter Plot)**
   - Scatter plot of claims vs. liabilities as % of GDP, colored by region.
   - Faceted by liability size bands.
   - Checkbox or dropdown for highlighting specific countries (e.g., “Mexico,” “United States”).
   - Beyond tooltip: uses dropdown and conditional highlighting.

4. **Global Network Heatmap or Chorddiagram**
   - Matrix (heatmap) of reporting countries vs. counterparties (regions or countries).
   - Hover and tooltip to reveal claim values; potential dropdown to toggle between “Claims” and “Liabilities.”


----------------------------------------------------------
|  Title: "The Global Web of Borrowing and Lending"       |
|  Intro paragraph explaining globalization of finance    |
----------------------------------------------------------
|  [ Chart 1: Global Claims and Liabilities Over Time ]   |
|  Dropdown: [All / Region / Income Group]                |
----------------------------------------------------------
|  [ Chart 2: Exposures by Income Group ]                 |
|  Slider: [← 2000  —  2024 →]                            |
----------------------------------------------------------
|  [ Chart 3: Claims vs. Liabilities (Scatter) ]          |
|  Dropdown: [Highlight Country]                          |
----------------------------------------------------------
|  [ Chart 4: Heatmap of Global Lending Network ]         |
|  Dropdown: [Claims / Liabilities]                       |
----------------------------------------------------------

## Data Sources

### Data Source 1: Locational banking statistics

URL: https://data.bis.org/topics/LBS

Size*: 42,000 rows, 6 columns
*Approx size because the data is presented in wide format and I am assuming an extra column for making it long format.

The locational banking statistics (LBS) measure international banking activity from a residence perspective, focusing on the location of the banking office.  The LBS capture the outstanding claims (financial assets) and liabilities of internationally active banks located in reporting countries on counterparties residing in more than 200 countries. Banks record their positions on an unconsolidated basis, including intragroup positions between offices of the same banking group. The LBS capture around 95% of all cross-border banking activity.

The data is published in US dollars, quarterly, with timeseries since 1980 and it is accesible through API. I am planning to use the last 10 years for the timeseries. This dataset contains the cross-country expositions. For the interactive visualization I am planning to use the more granular data that differentiates between type of product, type of counterparty and currency.

## Questions

1. Do you have any advice on useful/cool visualizations for networks or simulations that you rememeber? This could be added to my inspiration search.