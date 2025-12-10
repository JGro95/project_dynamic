import sys
import subprocess
from pathlib import Path


def run_step(script_name: str) -> None:
    """
    Helper to run a Python script inside the `cleaning` directory.
    """
    base_dir = Path(__file__).resolve().parent
    script_path = base_dir / "cleaning" / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    print(f"\n[GLOBAL FLOW] Running {script_name} ...")
    subprocess.run([sys.executable, str(script_path)], check=True)
    print(f"[GLOBAL FLOW] Finished {script_name}")


def main():
    """
    Runs the files for data download, cleaning, and chart-spec generation
    for the interactive visualizations.
    """
    print("=== Starting BIS data pipeline ===")

    # 1. Download/cache raw BIS data
    run_step("get_data.py")

    # 2. Build data + spec for Chart 1 (Global Financial Growth Overview)
    run_step("chart_1.py")

    # 4. Build data for Chart Chord diagram
    run_step("chart_4.py")

    print("\n=== All cleaning and preprocessing steps completed successfully")
    print("Data JSON files are in `docs/data/` and Vega/Altair specs in `docs/charts/`.")


if __name__ == "__main__":
    main()
