import pandas as pd
from pathlib import Path

# Relative Paths setup
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "www/data"

RAW_CSV = BASE_DIR / "lbs_raw_claims_liabilities.csv"

# BIS URLs (claims + liabilities)

urls = [
    # Liabilities (L_POSITION = L)
    "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_LBS_D_PUB/1.0/Q.S.L.A.TO1.A.5J.A.AT+AU+BE+BH+BM+BR+BS+CA+CH+CL+CN+CW+CY+DE+DK+ES+FI+FR+GB+GG+GR+HK+ID+IE+IM+IN+IT+JE+JP+KR+KY+LU+MO+MX+MY+NL+NO+PA+PH+PT+RU+SA+SE+SG+TR+TW+US+ZA.A.AD+AE+AF+AG+AI+AL+AM+AN+AO+AR+AT+AU+AW+BB+BD+BE+BF+BG+BH+BI+BJ+BM+BN+BO+BR+BS+BW+BY+BZ+C9+CA+CD+CF+CG+CH+CL+CM+CN+CO+CR+CS+CU+CV+CY+CZ+DD+DE+DK+DM+DO+DZ+EC+EE+EG+ES+ET+FI+FJ+FM+FR+GA+GB+GD+GE+GH+GI+GL+GN+GR+GT+GY+HK+HN+HR+HT+HU+ID+IE+IL+IN+IQ+IR+IS+IT+JM+JO+JP+KE+KG+KH+KI+KP+KR+KY+LA+LK+LT+LU+LV+LY+MA+MD+MG+MM+MN+MR+MV+MW+MX+MY+NA+NE+NG+NI+NL+NO+NP+NZ+PA+PE+PG+PH+PK+PL+PS+PT+PY+QA+RO+RS+RU+RW+SA+SD+SE+SG+SI+SK+SN+SO+SR+SS+SU+SV+SY+TH+TN+TR+TT+UA+UG+US+UY+VA+VE+VG+VN+WS+YE+YU+ZA.N?startPeriod=2000-10-16&endPeriod=2025-10-16&format=csv",
    # Claims (L_POSITION = C)
    "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_LBS_D_PUB/1.0/Q.S.C.A.TO1.A.1G+3W+3X+3Y+3Z+5J+5M+5N+AT+AU+BE+BH+BM+BR+BS+CA+CH+CL+CN+CY+DE+DK+ES+FI+FR+GB+GR+HK+ID+IE+IM+IN+IT+JE+JP+KR+KY+LU+MO+MX+MY+NL+NO+PA+PT+SE+SG+TR+TW+US+ZA.A.5A+AT+AU+BE+BH+BM+BR+BS+CA+CH+CL+CN+CY+DE+DK+ES+FI+FR+GB+GG+GR+HK+ID+IE+IM+IN+IT+JE+JP+KR+KY+LU+MO+MX+MY+NL+NO+PA+PH+PT+RU+SA+SE+SG+TR+TW+US+ZA.A.AD+AE+AF+AG+AI+AL+AM+AO+AR+AT+AU+AW+AZ+BA+BB+BD+BE+BG+BH+BI+BM+BN+BO+BR+BS+BW+BY+BZ+CA+CD+CF+CG+CH+CL+CM+CN+CO+CR+CU+CV+CZ+DE+DK+DM+DO+DZ+EC+EE+EG+ER+ES+ET+FI+FJ+FM+FR+GB+GE+GH+GL+GN+GQ+GR+GT+GY+HK+HN+HR+HT+HU+ID+IE+IL+IN+IQ+IR+IS+IT+JE+JM+JO+JP+KE+KG+KH+KP+KR+KY+KZ+LA+LB+LC+LK+LR+LT+LU+LV+LY+MA+MD+ME+MG+MH+MK+MM+MN+MO+MU+MV+MW+MX+MY+NA+NE+NG+NI+NL+NO+NP+NZ+OM+PA+PE+PF+PH+PK+PL+PS+PT+PY+QA+RO+RS+RU+RW+SA+SD+SE+SG+SI+SK+SN+SO+SR+SS+SV+SY+SZ+TC+TD+TF+TG+TH+TJ+TL+TM+TN+TO+TR+TT+TV+TW+TZ+UA+UG+US+UY+UZ+VA+VC+VE+VG+VN+WS+YE+ZA+ZM+ZW.N?startPeriod=2000-10-15&endPeriod=2025-10-15&format=csv",
]


# Download & cache raw BIS CSV data

if RAW_CSV.exists():
    print(f"Loading cached raw data from {RAW_CSV}")
    df = pd.read_csv(RAW_CSV)
else:
    print("Downloading BIS LBS data from API ...")
    df = pd.concat([pd.read_csv(url) for url in urls], ignore_index=True)
    df.to_csv(RAW_CSV, index=False)
    print(f"Saved raw data to {RAW_CSV}")

