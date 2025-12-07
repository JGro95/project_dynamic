import pandas as pd
from pathlib import Path
import json

#  Paths 
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "www" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_CSV = BASE_DIR / "lbs_raw_claims_liabilities.csv"
ISO_CODES = BASE_DIR / "concepts" / "countries_iso_codes.csv"

OUTPUT_JSON = DATA_DIR / "chart4_chord_all.json"

#  Load & prepare data in matrix format

print(f"Loading BIS LBS raw data from {RAW_CSV}")
df = pd.read_csv(RAW_CSV)

iso_codes = pd.read_csv(ISO_CODES)

# Convert TIME_PERIOD to quarter-end date
df["date"] = pd.PeriodIndex(df["TIME_PERIOD"], freq="Q").to_timestamp(how="end")

# Merge reporting country metadata
df = df.merge(
    iso_codes.add_suffix("_rep"),
    left_on="L_REP_CTY",
    right_on="ISO_2_rep",
    how="inner",
)

# Merge counterparty country metadata
df = df.merge(
    iso_codes.add_suffix("_cp"),
    left_on="L_CP_COUNTRY",
    right_on="ISO_2_cp",
    how="inner",
)

# Keep only cross-border claims (lender = reporting, borrower = counterparty)
df = df[df["L_POSITION"] == "C"].copy()

# Ensure clean labels
df["region_rep"] = df["region_rep"].fillna("Other / Unknown")
df["region_cp"] = df["region_cp"].fillna("Other / Unknown")
df["country_name_rep"] = df["country_name_rep"].fillna("Unknown")
df["country_name_cp"] = df["country_name_cp"].fillna("Unknown")

# For numeric stability, get exposures in trillion of USD
df["amount"] = df["OBS_VALUE"] / 1e6

# Get sorted list of unique dates as ISO strings
dates = sorted(df["date"].unique())
date_keys = [pd.Timestamp(d).date().isoformat() for d in dates]
print(f"Number of quarters: {len(date_keys)}")


# Subset of countries to focus (top N and Mexico)
N_FOCUS = 15  # base number of top countries

latest_date = df["date"].max()
df_latest = df[df["date"] == latest_date]

rep_totals_latest = (
    df_latest.groupby("country_name_rep", observed=True)["amount"]
    .sum()
    .sort_values(ascending=False)
)

focus_countries = rep_totals_latest.head(N_FOCUS).index.tolist()

# Make sure "Mexico" is included 
if "Mexico" not in focus_countries:
    focus_countries.append("Mexico")


print("Number of focus countries:", len(focus_countries))  
print("Top focus countries:", focus_countries)

# Compute total global funding (latest quarter only)
total_global = df_latest["amount"].sum()

# Compute total funding for the selected focus countries (top N + Mexico)
total_focus = (
    df_latest[df_latest["country_name_rep"].isin(focus_countries)]["amount"].sum()
)

share = (total_focus / total_global * 100) if total_global > 0 else 0

print(
    f"Focus countries represent {share:,.2f}% of global cross-border claims in {latest_date.date()} "
    f"({total_focus:,.2f} tn out of {total_global:,.2f} tn)."
)

# Helper: build matrix given node order and long-form edges 

def build_matrix(nodes, from_col, to_col, value_col, edges_df):
    """
    nodes: list of node labels
    from_col, to_col: column names in edges_df for source/target
    value_col: column name with numeric value
    edges_df: long df with one row per flow (from, to, value)
    """
    node_index = {name: i for i, name in enumerate(nodes)}
    n = len(nodes)
    mat = [[0.0] * n for _ in range(n)]

    for _, row in edges_df.iterrows():
        src = row[from_col]
        tgt = row[to_col]
        val = row[value_col]
        if src in node_index and tgt in node_index:
            i = node_index[src]
            j = node_index[tgt]
            mat[i][j] += float(val)

    return mat


# PREPPARE DATA DEPENDING ON VIEW / MODE
# OPTION 1: REGION to REGION 

# All regions ever present
all_regions = sorted(
    set(df["region_rep"]).union(df["region_cp"])
)

region_region = {
    "nodes": all_regions,
    "dates": date_keys,
    "matrices": {}
}

for d, d_key in zip(dates, date_keys):
    d_mask = df["date"] == d
    df_d = df.loc[d_mask, ["region_rep", "region_cp", "amount"]]

    # Aggregate by region pair
    edges = (
        df_d.groupby(["region_rep", "region_cp"], observed=True)["amount"]
        .sum()
        .reset_index()
    )

    mat = build_matrix(
        nodes=all_regions,
        from_col="region_rep",
        to_col="region_cp",
        value_col="amount",
        edges_df=edges,
    )

    region_region["matrices"][d_key] = mat

#  OPTION 2: COUNTRY to REGION (countries as sources)

country_region_nodes = focus_countries + all_regions

country_region = {
    "nodes": country_region_nodes,
    "dates": date_keys,
    "matrices": {}
}

for d, d_key in zip(dates, date_keys):
    df_d = df[df["date"] == d].copy()

    # restrict to focus countries as reporters
    df_d = df_d[df_d["country_name_rep"].isin(focus_countries)]

    edges = (
        df_d.groupby(["country_name_rep", "region_cp"], observed=True)["amount"]
        .sum()
        .reset_index()
        .rename(columns={
            "country_name_rep": "from",
            "region_cp": "to"
        })
    )

    mat = build_matrix(
        nodes=country_region_nodes,
        from_col="from",
        to_col="to",
        value_col="amount",
        edges_df=edges,
    )

    country_region["matrices"][d_key] = mat

# OPTION 3: COUNTRY to COUNTRY 

OTHER_BUCKET = "Other countries"
country_country_nodes = focus_countries + [OTHER_BUCKET]

country_country = {
    "nodes": country_country_nodes,
    "dates": date_keys,
    "matrices": {}
}

for d, d_key in zip(dates, date_keys):
    df_d = df[df["date"] == d].copy()

    # Only flows where reporter is a focus country
    df_d = df_d[df_d["country_name_rep"].isin(focus_countries)].copy()

    # Bucket counterparties:
    def bucket_cp(name):
        if name in focus_countries:
            return name
        else:
            return OTHER_BUCKET

    df_d["cp_bucket"] = df_d["country_name_cp"].map(bucket_cp)

    edges = (
        df_d.groupby(["country_name_rep", "cp_bucket"], observed=True)["amount"]
        .sum()
        .reset_index()
        .rename(columns={
            "country_name_rep": "from",
            "cp_bucket": "to"
        })
    )

    mat = build_matrix(
        nodes=country_country_nodes,
        from_col="from",
        to_col="to",
        value_col="amount",
        edges_df=edges,
    )

    country_country["matrices"][d_key] = mat

# Final JSON

output = {
    "meta": {
        "units": "USD trillions",
        "position": "Claims (reporting to counterparty)",
        "focus_countries": focus_countries,
    },
    "modes": {
        "region_region": region_region,
        "country_region": country_region,
        "country_country": country_country,
    },
}

OUTPUT_JSON.write_text(json.dumps(output, indent=2))
print(f"Saved chord data for all modes to {OUTPUT_JSON}")
