"""
add_nasa.py - adds a "NASA POWER Historical Check" tab to your Streamlit app.

Run once from the folder that contains app.py:
    python add_nasa.py
A backup of your current file is saved as app.py.before_nasa.
If the patched file has a syntax error, your original is restored automatically.
"""
import py_compile
import re
import shutil
import sys

SRC = "app.py"
BACKUP = "app.py.before_nasa"

# ---- Block 1: helper functions, inserted before the dashboard header ------------
FUNCS = '''# --- 5b. NASA POWER (historical hourly solar & weather) ---
from datetime import datetime, timedelta, timezone

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nasa_power_hourly(lat, lon, start, end):
    """Hourly NASA POWER data for one point. start/end are 'YYYYMMDD' strings (UTC)."""
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M,WS10M,WD10M,PS",
        "community": "RE",
        "longitude": round(float(lon), 4),
        "latitude": round(float(lat), 4),
        "start": start,
        "end": end,
        "format": "JSON",
        "time-standard": "UTC",
    }
    try:
        res = requests.get(NASA_POWER_URL, params=params, timeout=30)
        if res.status_code != 200:
            return None, "NASA POWER answered with HTTP " + str(res.status_code)
        data = res.json().get("properties", {}).get("parameter", {})
        if not data:
            return None, "NASA POWER returned no data for this request"
        df = pd.DataFrame(data)
        df.index = pd.to_datetime(df.index, format="%Y%m%d%H")
        df = df.replace(-999, np.nan).dropna()
        if df.empty:
            return None, "NASA POWER has not published these days yet"
        return df, "OK"
    except Exception as e:
        return None, str(e)


def nasa_row_to_telemetry(r):
    """Convert one NASA POWER row into the field names build_feature_vector expects."""
    rad = float(r["ALLSKY_SFC_SW_DWN"])
    return {
        "shortwave_radiation": rad,
        "temperature_2m": float(r["T2M"]),
        "relative_humidity_2m": float(r["RH2M"]),
        "pressure_msl": float(r["PS"]) * 10.0,       # kPa -> hPa (surface pressure)
        "wind_speed_10m": float(r["WS10M"]) * 3.6,   # m/s -> km/h
        "wind_direction_10m": float(r["WD10M"]),
        "is_day": 1 if rad > 5 else 0,
    }


'''

# ---- Block 2: the new tab, appended at the end of the file ----------------------
TAB = '''
# ==========================================
# TAB 3: NASA POWER HISTORICAL CHECK
# ==========================================
with tab_nasa:
    st.subheader("🛰️ NASA POWER: Past Week at the Selected Location")
    st.caption(
        "NASA POWER publishes satellite- and model-based hourly data a few days behind real time, "
        "so this tab looks at the week ending 3 days ago. Times are UTC. Cloud cover is not "
        "taken from NASA here, so the model uses its default cloud values; irradiance already "
        "reflects clouds."
    )

    # lat/lon are set in the first tab when a location has been found
    sel_lat = globals().get("lat")
    sel_lon = globals().get("lon")

    if sel_lat is None or sel_lon is None:
        st.info("Pick a location in the first tab to see its NASA POWER history.")
    else:
        end_d = datetime.now(timezone.utc).date() - timedelta(days=3)
        start_d = end_d - timedelta(days=6)
        with st.spinner("Requesting hourly data from NASA POWER..."):
            nasa_df, nasa_msg = fetch_nasa_power_hourly(
                sel_lat, sel_lon, start_d.strftime("%Y%m%d"), end_d.strftime("%Y%m%d")
            )

        if nasa_df is None:
            st.warning("Could not load NASA POWER data (" + str(nasa_msg) + "). Please try again later.")
        else:
            n_rows = [build_feature_vector(nasa_row_to_telemetry(r)).iloc[0]
                      for _, r in nasa_df.iterrows()]
            X_nasa = pd.DataFrame(n_rows, columns=features)
            n_pred = np.clip(model.predict(X_nasa), 0, None)
            n_pred[nasa_df["ALLSKY_SFC_SW_DWN"].to_numpy() <= 0] = 0.0

            k1, k2, k3 = st.columns(3)
            k1.metric("Peak irradiance", f"{nasa_df['ALLSKY_SFC_SW_DWN'].max():.0f} W/m²")
            k2.metric("Peak model power", f"{n_pred.max():,.0f} kW")
            k3.metric("Estimated energy", f"{n_pred.sum() / 1000:,.1f} MWh")

            st.markdown("#### ☀️ Surface irradiance (NASA POWER)")
            st.line_chart(nasa_df[["ALLSKY_SFC_SW_DWN"]].rename(
                columns={"ALLSKY_SFC_SW_DWN": "Irradiance (W/m²)"}))

            st.markdown("#### ⚡ Power the model estimates from NASA inputs")
            st.line_chart(pd.DataFrame({"Predicted power (kW)": n_pred}, index=nasa_df.index))

            st.caption(
                "Source: NASA POWER hourly API. Data covers " + str(start_d) + " to " + str(end_d) + "."
            )
'''


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()

    if "fetch_nasa_power_hourly" in text:
        sys.exit("The NASA tab is already in app.py. Nothing was changed.")

    # 1) insert helper functions before the dashboard header
    marker = "# --- 6. Dashboard Header ---"
    pos = text.find(marker)
    if pos == -1:
        m = re.search(r'^st\.markdown\("# ', text, flags=re.M)
        if not m:
            sys.exit("Could not find where to insert the NASA code. Nothing was changed.")
        pos = m.start()
    new = text[:pos] + FUNCS + text[pos:]

    # 2) add a third tab
    pattern = re.compile(r"tab_live\s*,\s*tab_manual\s*=\s*st\.tabs\(\s*\[(.*?)\]\s*\)", re.S)
    m = pattern.search(new)
    if not m:
        sys.exit("Could not find the st.tabs([...]) line. Nothing was changed.")
    inner = m.group(1).rstrip().rstrip(",")
    replacement = (
        "tab_live, tab_manual, tab_nasa = st.tabs([" + inner
        + ',\n    "🛰️ NASA POWER Historical Check"\n])'
    )
    new = new[:m.start()] + replacement + new[m.end():]

    # 3) append the tab body
    new = new.rstrip("\n") + "\n\n" + TAB.strip("\n") + "\n"

    shutil.copy(SRC, BACKUP)
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(new)

    try:
        py_compile.compile(SRC, doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy(BACKUP, SRC)
        sys.exit("The patched file had a syntax error, so your original was restored.\n" + str(e))

    print("Done. NASA POWER tab added (backup saved as " + BACKUP + ").")


if __name__ == "__main__":
    main()
