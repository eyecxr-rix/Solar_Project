"""
fix_nasa_lag.py - makes the NASA POWER tab find the most recent week that NASA has
actually published, instead of assuming a fixed 3-day lag.

Run once from the folder that contains app.py (after add_nasa.py):
    python fix_nasa_lag.py
A backup is saved as app.py.before_nasa_fix. If anything goes wrong your file is restored.
"""
import py_compile
import shutil
import sys

SRC = "app.py"
BACKUP = "app.py.before_nasa_fix"

REPLACEMENTS = [
    # 1) ask for a long window, then keep the latest 7 published days
    (
        '''        end_d = datetime.now(timezone.utc).date() - timedelta(days=3)
        start_d = end_d - timedelta(days=6)
        with st.spinner("Requesting hourly data from NASA POWER..."):
            nasa_df, nasa_msg = fetch_nasa_power_hourly(
                sel_lat, sel_lon, start_d.strftime("%Y%m%d"), end_d.strftime("%Y%m%d")
            )
''',
        '''        req_end = datetime.now(timezone.utc).date() - timedelta(days=2)
        req_start = req_end - timedelta(days=240)
        with st.spinner("Requesting hourly data from NASA POWER (this can take a few seconds)..."):
            nasa_df, nasa_msg = fetch_nasa_power_hourly(
                sel_lat, sel_lon, req_start.strftime("%Y%m%d"), req_end.strftime("%Y%m%d")
            )
        if nasa_df is not None:
            # keep only the most recent 7 days that NASA has actually published
            nasa_df = nasa_df[nasa_df.index > nasa_df.index.max() - timedelta(days=7)]
            start_d = nasa_df.index.min().date()
            end_d = nasa_df.index.max().date()
''',
    ),
    # 2) honest caption
    (
        '''        "NASA POWER publishes satellite- and model-based hourly data a few days behind real time, "
        "so this tab looks at the week ending 3 days ago. Times are UTC. Cloud cover is not "
''',
        '''        "NASA POWER publishes hourly solar data behind real time (sometimes by weeks or months), "
        "so this tab shows the most recent week NASA has published. Times are UTC. Cloud cover is not "
''',
    ),
    # 3) longer timeout for the bigger request
    ("res = requests.get(NASA_POWER_URL, params=params, timeout=30)",
     "res = requests.get(NASA_POWER_URL, params=params, timeout=60)"),
    # 4) clearer message
    ('return None, "NASA POWER has not published these days yet"',
     'return None, "NASA POWER has no published hourly solar data for this location in the last 8 months"'),
]


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()

    if "req_start = req_end" in text:
        sys.exit("This fix is already applied. Nothing was changed.")

    new = text
    for old, repl in REPLACEMENTS:
        if old not in new:
            sys.exit("Could not find the expected NASA code in app.py (did you edit it?). Nothing was changed.")
        new = new.replace(old, repl, 1)

    shutil.copy(SRC, BACKUP)
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(new)

    try:
        py_compile.compile(SRC, doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy(BACKUP, SRC)
        sys.exit("The patched file had a syntax error, so your original was restored.\n" + str(e))

    print("Done. The NASA tab now finds the latest published week (backup: " + BACKUP + ").")


if __name__ == "__main__":
    main()
