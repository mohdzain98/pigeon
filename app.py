# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import pdfkit
import tempfile
import os

st.set_page_config(page_title="Time Difference (Sum) Calculator", layout="centered")
st.title("🕒 Time Difference Sum Calculator — with PDF Download")

# Initialize session state for added times
if "times" not in st.session_state:
    st.session_state.times = []


# Helpers
def time_display(hour: int, minute: int, ampm: str) -> str:
    return f"{hour:02d}:{minute:02d} {ampm.upper()}"


def parts_to_datetime(hour: int, minute: int, ampm: str) -> datetime:
    ampm = ampm.upper()
    h24 = hour % 12
    if ampm == "PM":
        h24 += 12
    base = datetime.combine(date.today(), datetime.min.time())
    return base.replace(hour=h24, minute=minute, second=0, microsecond=0)


# Start time inputs
st.subheader("Set Start Time")
scol1, scol2, scol3 = st.columns([1, 1, 1])
with scol1:
    start_hour = st.number_input(
        "Start hour (1-12)", 1, 12, 6, 1, format="%d", key="start_h"
    )
with scol2:
    start_min = st.number_input(
        "Start minutes (0-59)", 0, 59, 15, 1, format="%d", key="start_m"
    )
with scol3:
    start_ampm = st.selectbox("Start AM/PM", ["AM", "PM"], index=0, key="start_ap")

st.markdown("---")
st.subheader("Add a Time")
acol1, acol2, acol3, acol4 = st.columns([1, 1, 1, 1])
with acol1:
    add_hour = st.number_input("Hour (1-12)", 1, 12, 5, 1, format="%d", key="add_h")
with acol2:
    add_min = st.number_input("Minutes (0-59)", 0, 59, 52, 1, format="%d", key="add_m")
with acol3:
    add_ampm = st.selectbox("AM/PM", ["AM", "PM"], index=1, key="add_ap")
with acol4:
    if st.button("➕ Add Time"):
        display = time_display(int(add_hour), int(add_min), add_ampm)
        st.session_state.times.append(
            {
                "display": display,
                "hour": int(add_hour),
                "minute": int(add_min),
                "ampm": add_ampm.upper(),
            }
        )

# Controls
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    if st.button("↩️ Remove Last"):
        if st.session_state.times:
            st.session_state.times.pop()
with c2:
    if st.button("🗑️ Clear All"):
        st.session_state.times = []
with c3:
    st.write(f"**{len(st.session_state.times)}** times added")

st.markdown("---")

if st.session_state.times:
    start_dt = parts_to_datetime(start_hour, start_min, start_ampm)
    rows = []
    total_seconds_sum = 0

    for entry in st.session_state.times:
        t_dt = parts_to_datetime(entry["hour"], entry["minute"], entry["ampm"])
        if t_dt < start_dt:
            t_dt += timedelta(days=1)

        diff = t_dt - start_dt
        secs = int(diff.total_seconds())
        total_seconds_sum += secs

        hours = secs // 3600
        minutes = (secs % 3600) // 60
        formatted = f"{hours} hours {minutes} minutes"
        hhmm = f"{hours:02d}:{minutes:02d}"

        rows.append(
            {
                "Added Time": entry["display"],
                "Difference from Start": formatted,
                "Diff (hh:mm)": hhmm,
            }
        )

    df = pd.DataFrame(rows)
    st.subheader("🧾 Times & Differences")
    st.dataframe(df, use_container_width=True)

    total_hours = total_seconds_sum // 3600
    total_minutes = (total_seconds_sum % 3600) // 60
    total_formatted = f"{total_hours} hours {total_minutes} minutes"
    st.markdown("---")
    st.subheader("🔢 Total (sum of all differences from start)")
    st.success(f"**{total_formatted}**")

    # Generate PDF
    if st.button("📄 Download as PDF"):
        html = f"""
        <html>
        <head><meta charset='utf-8'><style>
        table {{width:100%;border-collapse:collapse;}}
        th,td {{border:1px solid #888;padding:8px;text-align:center;}}
        th {{background-color:#f2f2f2;}}
        </style></head>
        <body>
        <h2>Time Difference Report</h2>
        <p><b>Start Time:</b> {time_display(start_hour, start_min, start_ampm)}</p>
        {df.to_html(index=False, escape=False)}
        <h3>Total Time: {total_formatted}</h3>
        </body></html>
        """
        config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdfkit.from_string(html, tmp.name, configuration=config)
            with open(tmp.name, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name="time_difference_report.pdf",
                    mime="application/pdf",
                )
            os.unlink(tmp.name)
else:
    st.info("Add times above to see and download your report.")
