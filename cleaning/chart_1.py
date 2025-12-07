import pandas as pd
import altair as alt
import json
from pathlib import Path

# Acknowledgments: I used ChatGPT to ask for examples of using the HTML signal and how to export the Vega/Altair docs.
# Relative Paths setup
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "docs/data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR = DATA_DIR.parent / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

RAW_CSV = BASE_DIR / "lbs_raw_claims_liabilities.csv"

SPEC_FILE = CHARTS_DIR / "chart1_spec.json"
PCT_SPEC_FILE = CHARTS_DIR / "chart1_pct_change_spec.json"
HHI_SPEC_FILE = CHARTS_DIR / "chart1_hhi_spec.json"

EXPOSURES_JSON = DATA_DIR / "chart1_exposures.json"
EXPOSURES_METADATA_JSON = DATA_DIR / "chart1_metadata.json"
ENTITY_JSON = DATA_DIR / "entity_options.json"

# Load raw data
df = pd.read_csv(RAW_CSV)

# Load auxiliary data (ISO codes & GDP)
iso_codes = pd.read_csv(BASE_DIR / "concepts" / "countries_iso_codes.csv")
gdp_2024 = pd.read_csv(BASE_DIR / "concepts" / "gdp_2024.csv")


# Aggregate to exposures_df
group_cols = ["L_POSITION", "L_REP_CTY", "L_CP_COUNTRY", "TIME_PERIOD"]

df2 = df.groupby(group_cols, observed=True, dropna=False)
exposures_df = df2["OBS_VALUE"].sum().reset_index().dropna()

# Drop aggregates / world region code 5A (if you don't want them)
exposures_df = exposures_df[exposures_df["L_REP_CTY"] != "5A"]

# Convert TIME_PERIOD (quarter) to actual timestamp
exposures_df["date"] = pd.PeriodIndex(
    exposures_df["TIME_PERIOD"], freq="Q"
).to_timestamp(how="end")

# Merge for reporting country (L_REP_CTY)
exposures_df = exposures_df.merge(
    iso_codes.add_suffix("_rep"),
    left_on="L_REP_CTY",
    right_on="ISO_2_rep",
    how="inner",
)

# Merge for counterparty country (L_CP_COUNTRY)
exposures_df = exposures_df.merge(
    iso_codes.add_suffix("_cp"),
    left_on="L_CP_COUNTRY",
    right_on="ISO_2_cp",
    how="inner",
)

# Merge 2024 GDP (for reporting country)
exposures_df = exposures_df.merge(
    gdp_2024,
    left_on="ISO_3_rep",
    right_on="Country_Code",
    how="inner",
)

exposures_df["gdp_2024"] = (
    pd.to_numeric(exposures_df["gdp_2024"], errors="coerce") / 1e6
)


# Keep only columns needed for Chart 1

cols_to_keep = [
    "date",
    "L_POSITION",
    "OBS_VALUE",
    "L_REP_CTY",
    "L_CP_COUNTRY",
    "country_name_rep",
    "ISO_2_rep",
    "ISO_3_rep",
    "region_rep",
]
cols_to_keep = [c for c in cols_to_keep if c in exposures_df.columns]

chart1_df = exposures_df[cols_to_keep].copy()

# OPTIMIZATION: Remove rows with zero OBS_VALUE to reduce file size
chart1_df_nonzero = chart1_df[chart1_df["OBS_VALUE"] != 0].copy()

# Create metadata file with country info (only unique combinations)
metadata_df = (
    chart1_df_nonzero[
        ["L_REP_CTY", "country_name_rep", "ISO_2_rep", "ISO_3_rep", "region_rep"]
    ]
    .drop_duplicates()
    .reset_index(drop=True)
)

# Save metadata as JSON
metadata_list = metadata_df.to_dict(orient="records")
with open(EXPOSURES_METADATA_JSON, "w") as f:
    json.dump(metadata_list, f, indent=2)

print(f"Saved metadata to {EXPOSURES_METADATA_JSON}")

# Create slim data file with only essential columns
slim_data_df = chart1_df_nonzero[
    ["date", "L_POSITION", "OBS_VALUE", "L_REP_CTY", "L_CP_COUNTRY"]
].copy()

# Save slim data as JSON for Vega/Altair
#    - orient='records' => list of {key: value} objects
#    - date_format='iso' => ISO 8601 timestamps so Vega can parse them as dates
# ------------------------------
slim_data_df.to_json(
    EXPOSURES_JSON,
    orient="records",
    date_format="iso",
)

print(f"Saved Chart 1 data to {EXPOSURES_JSON}")

# Prepare list of unique entities for dropdown menu
# Unique regions (drop NA)
regions = chart1_df["region_rep"].dropna().drop_duplicates().sort_values().tolist()

# Unique countries (drop NA)
countries = (
    chart1_df["country_name_rep"].dropna().drop_duplicates().sort_values().tolist()
)

entities = ["world"] + regions + countries

entity_options = (
    [{"value": "world", "label": "World"}]
    + [{"value": r, "label": r} for r in regions]
    + [{"value": c, "label": c} for c in countries]
)


with open(ENTITY_JSON, "w") as f:
    json.dump(entity_options, f, indent=2)

print("Saved entity options to:", ENTITY_JSON)


# build_chart1.py
data_source = alt.Data(
    url="data/chart1_exposures.json",
    format={"type": "json"},
)

metadata_source = alt.Data(
    url="data/chart1_metadata.json",
    format={"type": "json"},
)

# Params (controlled from HTML/JS)
entity_param = alt.param("entity", value="world")

# Hover selection
hover = alt.selection_point(
    fields=["date", "Position"],
    nearest=True,
    on="mouseover",
    empty="none",
)

# Base chart
base = (
    alt.Chart(data_source)
    .transform_lookup(
        lookup="L_REP_CTY",
        from_=alt.LookupData(
            data=metadata_source,
            key="L_REP_CTY",
            fields=["country_name_rep", "region_rep"],
        ),
    )
    .transform_filter(
        "entity == 'world' || datum.country_name_rep == entity || datum.region_rep == entity"
    )
    .transform_aggregate(
        total_obs="sum(OBS_VALUE)",
        groupby=["date", "L_POSITION"],
    )
    .transform_pivot(
        "L_POSITION",
        value="total_obs",
        groupby=["date"],
    )
    .transform_calculate(
        Claims="datum.C / 1e6",
        Liabilities="-datum.L / 1e6",
        Net="(datum.C - datum.L) / 1e6",
    )
    .transform_fold(
        ["Claims", "Liabilities", "Net"],
        as_=["Position", "Value"],
    )
    .encode(
        x=alt.X(
            "yearmonth(date):T", title="", axis=alt.Axis(format="%Y", labelFontSize=14)
        ),
        y=alt.Y("Value:Q", title="Trillion USD", axis=alt.Axis(labelFontSize=14, titleFontSize=14)),
        color=alt.Color(
            "Position:N",
            scale=alt.Scale(
                domain=["Claims", "Liabilities", "Net"],
                range=["#2A9D8F", "#B91C1C", "#282D28"],
            ),
            legend=alt.Legend(title="", orient="top", labelFontSize=15, symbolSize=250),
        ),
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%Y-%m"),
            alt.Tooltip("Position:N", title="Position"),
            alt.Tooltip("Value:Q", title="Amount (USD tn)", format=",.2f"),
        ],
    )
)

# Bars for claims and liabilities
bars = (
    base.transform_filter("datum.Position != 'Net'")
    .mark_bar()
    .encode(
        size=alt.condition(hover, alt.value(10), alt.value(8)),
        opacity=alt.condition(hover, alt.value(1.0), alt.value(0.6)),
    )
)

# Line for net position
line = base.transform_filter("datum.Position == 'Net'").mark_line(strokeWidth=3)

# Circles on the line that appear on hover
points = (
    base.transform_filter("datum.Position == 'Net'")
    .mark_circle(size=70)
    .encode(
        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
    )
)

# Combine layers and set properties
chart = (
    alt.layer(bars, line, points)
    .add_params(entity_param, hover)
    .properties(
        title="",
        width=1050,
        height=400,
    )
    .interactive()
)

chart.save(SPEC_FILE)
print(f"Saved chart spec to {SPEC_FILE}")


# Quarter-over-quarter percent change for claims and liabilities
pct_change_chart = (
    alt.Chart(data_source)
    .transform_lookup(
        lookup="L_REP_CTY",
        from_=alt.LookupData(
            data=metadata_source,
            key="L_REP_CTY",
            fields=["country_name_rep", "region_rep"],
        ),
    )
    .transform_filter(
        "entity == 'world' || datum.country_name_rep == entity || datum.region_rep == entity"
    )
    .transform_aggregate(
        total_obs="sum(OBS_VALUE)",
        groupby=["date", "L_POSITION"],
    )
    .transform_window(
        prev_total="lag(total_obs)",
        sort=[{"field": "date"}],
        groupby=["L_POSITION"],
    )
    .transform_calculate(
        pct_change=(
            "datum.prev_total ? "
            "(datum.total_obs - datum.prev_total) / datum.prev_total * 100 : null"
        ),
        Position="datum.L_POSITION == 'C' ? 'Claims' : 'Liabilities'",
    )
    .transform_filter("isValid(datum.pct_change)")
    .mark_line(point=True)
    .encode(
        x=alt.X("yearmonth(date):T", title="", axis=alt.Axis(format="%Y", labelFontSize=14)),
        y=alt.Y("pct_change:Q", title="Quarter-over-quarter change (%)", axis=alt.Axis(labelFontSize=14, titleFontSize=14)),
        color=alt.Color(
            "Position:N",
            scale=alt.Scale(
                domain=["Claims", "Liabilities"],
                range=["#2A9D8F", "#B91C1C"],
            ),
            legend=alt.Legend(title="", orient="top", labelFontSize=15, symbolSize=250),
        ),
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%Y-%m"),
            alt.Tooltip("Position:N", title="Position"),
            alt.Tooltip("pct_change:Q", title="QoQ change (%)", format=",.1f"),
        ],
    )
    .properties(
        title="",
        width=1050,
        height=300,
    )
    .add_params(entity_param)
)

pct_change_chart.save(PCT_SPEC_FILE)
print(f"Saved percent-change chart spec to {PCT_SPEC_FILE}")


# HHI concentration index from borrower (liabilities) perspective
hhi_chart = (
    alt.Chart(data_source)
    .transform_lookup(
        lookup="L_REP_CTY",
        from_=alt.LookupData(
            data=metadata_source,
            key="L_REP_CTY",
            fields=["country_name_rep", "region_rep"],
        ),
    )
    .transform_filter(
        "entity == 'world' || datum.country_name_rep == entity || datum.region_rep == entity"
    )
    .transform_filter("datum.L_POSITION == 'L'")
    .transform_aggregate(
        liability_by_cp="sum(OBS_VALUE)",
        groupby=["date", "L_CP_COUNTRY"],
    )
    .transform_joinaggregate(
        total_liabilities="sum(liability_by_cp)",
        groupby=["date"],
    )
    .transform_calculate(
        share=(
            "datum.total_liabilities > 0 ? "
            "datum.liability_by_cp / datum.total_liabilities : 0"
        ),
        share_sq="datum.share * datum.share",
    )
    .transform_aggregate(
        hhi="sum(share_sq)",
        groupby=["date"],
    )
    .transform_calculate(
        hhi_index="datum.hhi * 10000",
    )
    .mark_line(point=True)
    .encode(
        x=alt.X("yearmonth(date):T", title="", axis=alt.Axis(format="%Y", labelFontSize=14)),
        y=alt.Y("hhi_index:Q", title="HHI (0-10,000)", axis=alt.Axis(labelFontSize=14, titleFontSize=14)),
        color=alt.value("#2A2E34"),
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%Y-%m"),
            alt.Tooltip("hhi_index:Q", title="HHI", format=",.0f"),
        ],
    )
    .properties(
        title="",
        width=1050,
        height=400,
    )
    .add_params(entity_param)
)

hhi_chart.save(HHI_SPEC_FILE)
print(f"Saved HHI chart spec to {HHI_SPEC_FILE}")
