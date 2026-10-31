"""
fix_app.py - repairs a truncated app.py.

Your app.py stops in the middle of a string (line 578, "PEAK NOON SIMULATION (12:0"),
so Python raises "SyntaxError: unterminated string literal".

Run once from the folder that contains app.py:
    python fix_app.py
A backup of your original is saved as app.py.bak.
"""
import py_compile
import shutil
import sys

SRC = "app.py"

# ---- Block 1: everything that was missing inside `if api_data:` ----------------
MAIN = '''
day_badge = (
    "☀️ PEAK NOON SIMULATION (12:00 PM FORECAST)" if using_noon_sim
    else ("☀️ DAYTIME AT LOCATION" if (eff_is_day == 1 and eff_rad > 5)
          else "🌙 NIGHTTIME AT LOCATION (SOLAR IRRADIANCE = 0)")
)

import html

st.markdown(
    '<div class="sub-card">📍 <b>Target Locked:</b> ' + html.escape(place_title)
    + ' | <b>Coords:</b> ' + f"{lat:.4f}°, {lon:.4f}°"
    + ' | <b>Local Time:</b> ' + html.escape(f"{local_time_str} ({tz_name})")
    + ' | <b>Status:</b> ' + day_badge + '</div>',
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Solar Irradiance", f"{eff_rad:.1f} W/m²")
m2.metric("Ambient Temp", f"{float(active_telemetry.get('temperature_2m', 0)):.1f} °C")
m3.metric("Relative Humidity", f"{float(active_telemetry.get('relative_humidity_2m', 0)):.0f}%")
m4.metric("Cloud Cover", f"{float(active_telemetry.get('cloud_cover', 0)):.0f}%")
m5.metric("Wind Speed (10m)", f"{float(active_telemetry.get('wind_speed_10m', 0)):.1f} km/h")

# --- Prediction for the selected moment ---
X_live = build_feature_vector(active_telemetry)
if eff_is_day == 0 or eff_rad <= 0:
    pred_kw = 0.0
else:
    pred_kw = max(0.0, float(model.predict(X_live)[0]))

st.markdown(
    '<div class="metric-card"><h3>ESTIMATED SOLAR POWER OUTPUT — '
    + html.escape(short_name).upper() + '</h3>'
    + '<div style="font-size:3.4rem;font-weight:700;color:#38bdf8;">'
    + f"{pred_kw:,.2f}" + ' <span style="font-size:1.4rem;">kW</span></div></div>',
    unsafe_allow_html=True,
)

# --- Warn when live inputs fall outside what the model was trained on ---
live_row = X_live.iloc[0]
outside = [c for c in features if not (feat_mins[c] <= live_row[c] <= feat_maxs[c])]
if outside:
    st.warning(
        "Some live values are outside the range the model was trained on, "
        "so treat this estimate as rough: " + ", ".join(outside[:6])
    )
st.caption(
    "Indicative estimate from a Random Forest trained on one historical dataset; "
    "it is not calibrated to a specific plant at this location."
)

# --- 48-hour forecast ---
hourly = api_data.get("hourly", {})
h_times = hourly.get("time", [])
if h_times:
    h_rows = []
    h_rad = []
    for i in range(len(h_times)):
        d = {k: v[i] for k, v in hourly.items()
             if k != "time" and i < len(v) and v[i] is not None}
        h_rows.append(build_feature_vector(d).iloc[0])
        h_rad.append(float(d.get("shortwave_radiation", 0.0)))
    h_X = pd.DataFrame(h_rows, columns=features)
    h_pred = np.clip(model.predict(h_X), 0, None)
    h_pred[np.array(h_rad) <= 0] = 0.0
    st.markdown("#### 📈 48-Hour Power Forecast")
    st.line_chart(pd.DataFrame({"Predicted power (kW)": h_pred},
                               index=pd.to_datetime(h_times)))
'''

# ---- Block 2: `else` for `if api_data:` -----------------------------------------
ELSE_API = '''
else:
    st.error("Could not fetch live telemetry (" + str(status) + "). Please try again in a moment.")
'''

# ---- Block 3: `else` for `if matches:` ------------------------------------------
ELSE_MATCH = '''
else:
    st.warning("No matching location found. Try a nearby city or a different spelling.")
'''

# ---- Block 4: the manual tab (module level) -------------------------------------
MANUAL = '''
# ==========================================
# TAB 2: MANUAL TELEMETRY CONTROLS
# ==========================================
with tab_manual:
    st.subheader("🎛️ Manual Telemetry Controls & Feature Matrix")
    st.caption("Set every model input by hand to see how the Random Forest responds.")

    manual_vals = {}
    ctrl_cols = st.columns(3)
    for i, col_name in enumerate(features):
        lo = float(feat_mins[col_name])
        hi = float(feat_maxs[col_name])
        if hi <= lo:
            hi = lo + 1.0
        default = min(max(float(feat_defaults[col_name]), lo), hi)
        manual_vals[col_name] = ctrl_cols[i % 3].number_input(
            col_name, min_value=lo, max_value=hi, value=default, key="manual_" + col_name
        )

    X_manual = pd.DataFrame([manual_vals], columns=features)
    manual_kw = max(0.0, float(model.predict(X_manual)[0]))

    st.markdown(
        '<div class="metric-card"><h3>PREDICTED SOLAR POWER OUTPUT</h3>'
        '<div style="font-size:3.4rem;font-weight:700;color:#38bdf8;">'
        + f"{manual_kw:,.2f}" + ' <span style="font-size:1.4rem;">kW</span></div></div>',
        unsafe_allow_html=True,
    )

    with st.expander("🔬 Feature matrix sent to the model"):
        st.dataframe(X_manual.T.rename(columns={0: "value"}))

    st.caption(
        f"Random Forest · {record_count:,} training records · hold-out R² = {model_r2:.1f}%"
    )
'''


def indent(block, n):
    pad = " " * n
    out = [(pad + ln) if ln.strip() else ln for ln in block.strip("\n").split("\n")]
    return "\n".join(out) + "\n"


def main():
    with open(SRC, encoding="utf-8") as f:
        lines = f.read().split("\n")

    hits = [i for i, ln in enumerate(lines) if ln.strip() == "day_badge = ("]
    if not hits:
        sys.exit('Could not find the line "day_badge = (" in app.py. Nothing was changed.')

    cut = hits[-1]
    base = len(lines[cut]) - len(lines[cut].lstrip())
    if base < 8:
        sys.exit("Unexpected indentation around day_badge. Nothing was changed.")

    shutil.copy(SRC, SRC + ".bak")
    new = (
        "\n".join(lines[:cut]) + "\n"
        + indent(MAIN, base)
        + indent(ELSE_API, base - 4)
        + "\n"
        + indent(ELSE_MATCH, base - 8)
        + "\n"
        + MANUAL.strip("\n") + "\n"
    )
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(new)

    try:
        py_compile.compile(SRC, doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy(SRC + ".bak", SRC)
        sys.exit("The patched file still had a syntax error, so your original was restored.\n" + str(e))

    print("Done. app.py is repaired (backup saved as app.py.bak).")


if __name__ == "__main__":
    main()
