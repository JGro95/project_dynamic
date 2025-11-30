import json
from pathlib import Path

import altair as alt
import pandas as pd

# Acknowledgments: I used ChatGPT to ask for examples of using the HTML signal and how to export the Vega/Altair docs. This plot was difficult to render for the space and chatGPT also helped with that.
# Paths

BASE_DIR = Path(__file__).resolve().parent         
DATA_DIR = BASE_DIR.parent / "www" / "data"     
CHARTS_DIR = BASE_DIR.parent / "www" / "charts"

DATA_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

RAW_CSV = BASE_DIR / "lbs_raw_claims_liabilities.csv"
ISO_CODES_CSV = BASE_DIR / "concepts" / "countries_iso_codes.csv"
GDP_2024_CSV = BASE_DIR / "concepts" / "gdp_2024.csv"

CHART2_JSON = DATA_DIR / "chart2_exposures.json"
REGION_OPTIONS_JSON = DATA_DIR / "region_options.json"
INCOME_OPTIONS_JSON = DATA_DIR / "income_options.json"
SPEC_FILE = CHARTS_DIR / "chart2_spec.json"


# Load raw data

print("Loading raw BIS LBS data from:", RAW_CSV)
df = pd.read_csv(RAW_CSV)

iso_codes = pd.read_csv(ISO_CODES_CSV)
gdp_2024 = pd.read_csv(GDP_2024_CSV)

group_cols = ["L_POSITION", "L_REP_CTY", "L_CP_COUNTRY", "TIME_PERIOD"]
df2 = df.groupby(group_cols, observed=True, dropna=False)
exposures_df = df2["OBS_VALUE"].sum().reset_index().dropna()

# Drop aggregates (e.g., world region code '5A') if desired
exposures_df = exposures_df[exposures_df["L_REP_CTY"] != "5A"]

# Quarter -> timestamp
exposures_df["date"] = (
    pd.PeriodIndex(exposures_df["TIME_PERIOD"], freq="Q")
    .to_timestamp(how="end")
)

# --- Merge reporting country metadata (rep) ---
exposures_df = exposures_df.merge(
    iso_codes.add_suffix("_rep"),
    left_on="L_REP_CTY",
    right_on="ISO_2_rep",
    how="left",
)

# --- Merge counterparty country metadata (cp) ---
exposures_df = exposures_df.merge(
    iso_codes.add_suffix("_cp"),
    left_on="L_CP_COUNTRY",
    right_on="ISO_2_cp",
    how="left",
)

# --- Merge GDP (reporting side) ---
exposures_df = exposures_df.merge(
    gdp_2024,
    left_on="ISO_3_rep",
    right_on="Country_Code",
    how="left",
)

exposures_df["gdp_2024"] = (
    pd.to_numeric(exposures_df["gdp_2024"], errors="coerce") / 1e6
)




# Build dataset for chart 2 
chart2_df = exposures_df[[
    "date",
    "L_POSITION",
    "OBS_VALUE",
    "region_rep",
    "income_group_rep",
    "country_name_rep",
]].dropna(subset=["region_rep", "income_group_rep"])

chart2_df.to_json(
    CHART2_JSON,
    orient="records",
    date_format="iso",
)
print(f"Saved Chart 2 data to {CHART2_JSON}")

# -----------------------------
# 3. Opciones de región / ingreso para dropdowns
# -----------------------------
regions = (
    chart2_df["region_rep"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

income_groups = (
    chart2_df["income_group_rep"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

region_options = [{"value": "all", "label": "All regions"}] + [
    {"value": r, "label": r} for r in regions
]

income_options = [{"value": "all", "label": "All income groups"}] + [
    {"value": g, "label": g} for g in income_groups
]

with open(REGION_OPTIONS_JSON, "w", encoding="utf-8") as f:
    json.dump(region_options, f, ensure_ascii=False, indent=2)

with open(INCOME_OPTIONS_JSON, "w", encoding="utf-8") as f:
    json.dump(income_options, f, ensure_ascii=False, indent=2)

print(f"Saved region options to {REGION_OPTIONS_JSON}")
print(f"Saved income-group options to {INCOME_OPTIONS_JSON}")

# -----------------------------
# 4. Altair/Vega spec para Chart 2
# -----------------------------
data_source = alt.Data(
    url="data/chart2_exposures.json",
    format={"type": "json"},
)

# entity param from HTMLdropdown de HTML
entity_param = alt.param("entity", value="world")

# --- REGION ---
region_chart = (
    alt.Chart(data_source)
    .transform_filter(
        # Si entity == 'world', no filtro; si no, comparo con region_rep o country_name_rep
        "entity == 'world' || datum.region_rep == entity || datum.country_name_rep == entity"
    )
    .transform_aggregate(
        total_obs="sum(OBS_VALUE)",
        groupby=["date", "L_POSITION", "region_rep"],
    )
    .transform_calculate(
        Position="datum.L_POSITION == 'C' ? 'Claims' : 'Liabilities'",
        total_obs_tn="datum.total_obs / 1e6",
    )
    .mark_area()
    .encode(
        x=alt.X(
            "yearmonth(date):T",
            title="Date",
            axis=alt.Axis(format="%Y-%m"),
        ),
        y=alt.Y(
            "total_obs_tn:Q",
            title="Trillion USD",
        ),
        color=alt.Color(
            "region_rep:N",
            title="Region",
            scale=alt.Scale(
                domain=[
                    "Europe & Central Asia",
                    "East Asia & Pacific",
                    "Latin America & Caribbean",
                    "North America",
                    "Sub-Saharan Africa",
                ],
                range=["#1E3A8A", "#2A9D8F", "#268BD2", "#B58900", "#E76F51"],
            ),
        ),
        tooltip=[
            alt.Tooltip("yearquarter(date):T", title="Quarter"),
            alt.Tooltip("region_rep:N", title="Region"),
            alt.Tooltip("Position:N", title="Position"),
            alt.Tooltip("total_obs_tn:Q", title="Amount (USD tn)", format=",.2f"),
        ],
        facet=alt.Facet("Position:N"),
    )
    .properties(
        title="Cross-Border Claims and Liabilities by region",
        height=300,
    )
)

# --- INCOME GROUP ---
income_chart = (
    alt.Chart(data_source)
    .transform_filter(
        "entity == 'world' || datum.region_rep == entity || datum.country_name_rep == entity"
    )
    .transform_aggregate(
        total_obs="sum(OBS_VALUE)",
        groupby=["date", "L_POSITION", "income_group_rep"],
    )
    .transform_calculate(
        Position="datum.L_POSITION == 'C' ? 'Claims' : 'Liabilities'",
        total_obs_tn="datum.total_obs / 1e6",
    )
    .mark_area()
    .encode(
        x=alt.X(
            "yearmonth(date):T",
            title="Date",
            axis=alt.Axis(format="%Y-%m"),
        ),
        y=alt.Y(
            "total_obs_tn:Q",
            title="Trillion USD",
        ),
        color=alt.Color(
            "income_group_rep:N",
            title="Income group",
            scale=alt.Scale(
                domain=[
                    "High income",
                    "Upper middle income",
                    "Lower middle income",
                ],
                range=["#1E3A8A", "#B58900", "#E76F51"],
            ),
        ),
        tooltip=[
            alt.Tooltip("yearquarter(date):T", title="Quarter"),
            alt.Tooltip("income_group_rep:N", title="Income group"),
            alt.Tooltip("Position:N", title="Position"),
            alt.Tooltip("total_obs_tn:Q", title="Amount (USD tn)", format=",.2f"),
        ],
        facet=alt.Facet("Position:N"),
    )
    .properties(
        title="Cross-Border Claims and Liabilities by income group",
        height=300,
    )
)

# Combine region and incomeadding entity param
chart2 = (region_chart & income_chart).resolve_scale(color="independent")
chart2 = chart2.add_params(entity_param)

chart2.save(SPEC_FILE)
print(f"Saved Chart 2 spec to {SPEC_FILE}")