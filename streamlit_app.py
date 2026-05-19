import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Smart Factory KPI Dashboard",
    page_icon="🏭",
    layout="wide"
)

# ============================================================
# Load data
# ============================================================

@st.cache_data
def load_data():
    current_folder = Path(__file__).parent
    file_path = current_folder / "smart_factory_mes_dataset.xlsx"

    production_log = pd.read_excel(file_path, sheet_name="Production_Log")
    downtime_log = pd.read_excel(file_path, sheet_name="Downtime_Log")
    machine_master = pd.read_excel(file_path, sheet_name="Machine_Master")
    defect_log = pd.read_excel(file_path, sheet_name="Defect_Log")

    production_log["date"] = pd.to_datetime(production_log["date"])

    return production_log, downtime_log, machine_master, defect_log


production_log, downtime_log, machine_master, defect_log = load_data()

# ============================================================
# Helper functions
# ============================================================

def calculate_kpis(df):
    total_planned_output = df["planned_output"].sum()
    total_actual_output = df["actual_output"].sum()
    total_good_units = df["good_units"].sum()
    total_defective_units = df["defective_units"].sum()

    total_planned_minutes = df["planned_production_minutes"].sum()
    total_operating_minutes = df["operating_minutes"].sum()
    total_downtime_minutes = df["downtime_minutes"].sum()
    total_operating_hours = df["operating_hours"].sum()

    availability = (
        total_operating_minutes / total_planned_minutes
        if total_planned_minutes != 0 else 0
    )

    performance = (
        total_actual_output / total_planned_output
        if total_planned_output != 0 else 0
    )

    quality = (
        total_good_units / total_actual_output
        if total_actual_output != 0 else 0
    )

    oee = availability * performance * quality

    yield_rate = (
        total_good_units / total_actual_output
        if total_actual_output != 0 else 0
    )

    defect_rate = (
        total_defective_units / total_actual_output
        if total_actual_output != 0 else 0
    )

    uph = (
        total_actual_output / total_operating_hours
        if total_operating_hours != 0 else 0
    )

    downtime_rate = (
        total_downtime_minutes / total_planned_minutes
        if total_planned_minutes != 0 else 0
    )

    return {
        "total_planned_output": total_planned_output,
        "total_actual_output": total_actual_output,
        "total_good_units": total_good_units,
        "total_defective_units": total_defective_units,
        "total_downtime_hours": total_downtime_minutes / 60,
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "oee": oee,
        "yield_rate": yield_rate,
        "defect_rate": defect_rate,
        "uph": uph,
        "downtime_rate": downtime_rate
    }


def calculate_group_kpis(df, group_col):
    records = []

    for group_value, group_df in df.groupby(group_col):
        kpis = calculate_kpis(group_df)
        kpis[group_col] = group_value
        records.append(kpis)

    return pd.DataFrame(records)


def calculate_date_kpis(df):
    records = []

    for date_value, date_df in df.groupby("date"):
        kpis = calculate_kpis(date_df)
        kpis["date"] = date_value
        records.append(kpis)

    return pd.DataFrame(records)


def format_percent(value):
    return f"{value * 100:.2f}%"


def format_number(value):
    return f"{value:,.0f}"

def generate_daily_pdf_report(
    report_date,
    daily_kpis,
    top_downtime_reason,
    top_downtime_minutes,
    worst_machine,
    worst_machine_downtime,
    alert_status,
    daily_report
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Smart Factory Daily KPI Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Report Date: {report_date}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Executive summary
    story.append(Paragraph("1. Executive Summary", styles["Heading2"]))

    summary_text = (
        f"This automated daily report summarizes production performance, "
        f"OEE, yield, UPH, downtime, and alert status for {report_date}. "
        f"The report is generated from simulated MES-style production data."
    )

    story.append(Paragraph(summary_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # KPI table
    story.append(Paragraph("2. Daily KPI Summary", styles["Heading2"]))

    kpi_table_data = [
        ["Metric", "Value"],
        ["Total Planned Output", f"{daily_kpis['total_planned_output']:,.0f}"],
        ["Total Actual Output", f"{daily_kpis['total_actual_output']:,.0f}"],
        ["Total Good Units", f"{daily_kpis['total_good_units']:,.0f}"],
        ["Total Defective Units", f"{daily_kpis['total_defective_units']:,.0f}"],
        ["Total Downtime Hours", f"{daily_kpis['total_downtime_hours']:,.2f}"],
        ["Availability", f"{daily_kpis['availability'] * 100:.2f}%"],
        ["Performance", f"{daily_kpis['performance'] * 100:.2f}%"],
        ["Quality", f"{daily_kpis['quality'] * 100:.2f}%"],
        ["OEE", f"{daily_kpis['oee'] * 100:.2f}%"],
        ["Yield", f"{daily_kpis['yield_rate'] * 100:.2f}%"],
        ["Defect Rate", f"{daily_kpis['defect_rate'] * 100:.2f}%"],
        ["UPH", f"{daily_kpis['uph']:,.2f}"],
        ["Downtime Rate", f"{daily_kpis['downtime_rate'] * 100:.2f}%"],
    ]

    kpi_table = Table(kpi_table_data, colWidths=[220, 220])

    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(kpi_table)
    story.append(Spacer(1, 18))

    # Operational diagnostics
    story.append(Paragraph("3. Operational Diagnostics", styles["Heading2"]))

    diagnostic_table_data = [
        ["Item", "Result"],
        ["Top Downtime Reason", str(top_downtime_reason)],
        ["Top Downtime Minutes", f"{top_downtime_minutes:,.0f} minutes"],
        ["Worst Machine by Downtime", str(worst_machine)],
        ["Worst Machine Downtime", f"{worst_machine_downtime:,.0f} minutes"],
        ["Alert Status", str(alert_status)],
    ]

    diagnostic_table = Table(diagnostic_table_data, colWidths=[220, 220])

    diagnostic_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(diagnostic_table)
    story.append(Spacer(1, 18))

    # Alert interpretation
    story.append(Paragraph("4. Alert Interpretation", styles["Heading2"]))

    if alert_status == "Normal":
        alert_text = (
            "No critical threshold-based alert was triggered for the selected date. "
            "Production performance is considered within the expected monitoring range."
        )
    else:
        alert_text = (
            f"The system triggered the following alert(s): {alert_status}. "
            f"Further investigation should focus on OEE loss, downtime drivers, "
            f"yield performance, and machine-level constraints."
        )

    story.append(Paragraph(alert_text, styles["Normal"]))
    story.append(Spacer(1, 18))

    # Footer note
    story.append(Paragraph("5. Notes", styles["Heading2"]))

    note_text = (
        "This report is generated automatically by the Streamlit-based Smart Factory "
        "KPI Monitoring and Reporting Automation System. The dataset is simulated "
        "for portfolio and demonstration purposes."
    )

    story.append(Paragraph(note_text, styles["Normal"]))

    doc.build(story)

    buffer.seek(0)
    return buffer

# ============================================================
# Sidebar filters
# ============================================================

st.sidebar.title("Dashboard Filters")

min_date = production_log["date"].min()
max_date = production_log["date"].max()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

selected_lines = st.sidebar.multiselect(
    "Production Line",
    options=sorted(production_log["line_id"].unique()),
    default=sorted(production_log["line_id"].unique())
)

selected_shifts = st.sidebar.multiselect(
    "Shift",
    options=sorted(production_log["shift"].unique()),
    default=sorted(production_log["shift"].unique())
)

selected_products = st.sidebar.multiselect(
    "Product Type",
    options=sorted(production_log["product_type"].unique()),
    default=sorted(production_log["product_type"].unique())
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_production = production_log[
    (production_log["date"] >= pd.to_datetime(start_date)) &
    (production_log["date"] <= pd.to_datetime(end_date)) &
    (production_log["line_id"].isin(selected_lines)) &
    (production_log["shift"].isin(selected_shifts)) &
    (production_log["product_type"].isin(selected_products))
].copy()

if filtered_production.empty:
    st.title("🏭 Smart Factory KPI Monitoring Dashboard")
    st.warning("No data available under the selected filters.")
    st.stop()

valid_production_ids = filtered_production["production_id"].unique()

filtered_downtime = downtime_log[
    downtime_log["production_id"].isin(valid_production_ids)
].copy()

filtered_defect = defect_log[
    defect_log["production_id"].isin(valid_production_ids)
].copy()

downtime_analysis = filtered_downtime.merge(
    filtered_production[
        ["production_id", "date", "line_id", "shift", "product_type"]
    ],
    on="production_id",
    how="left"
)

defect_analysis = filtered_defect.merge(
    filtered_production[
        ["production_id", "date", "line_id", "shift", "product_type"]
    ],
    on="production_id",
    how="left"
)

overall_kpis = calculate_kpis(filtered_production)

# ============================================================
# Main title
# ============================================================

st.title("🏭 Smart Factory KPI Monitoring Dashboard")

st.caption(
    "A simulated MES-style manufacturing analytics dashboard for monitoring "
    "OEE, yield, UPH, downtime, and defect performance."
)

# ============================================================
# Navigation tabs
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Factory Overview",
    "2. OEE Loss Breakdown",
    "3. Downtime Root Cause",
    "4. Yield and Defect Analysis",
    "5. Automated Daily Report"
])

# ============================================================
# Tab 1: Factory Overview
# ============================================================

with tab1:
    st.header("Factory Performance Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Planned Output",
        format_number(overall_kpis["total_planned_output"])
    )

    col2.metric(
        "Total Actual Output",
        format_number(overall_kpis["total_actual_output"])
    )

    col3.metric(
        "Total Good Units",
        format_number(overall_kpis["total_good_units"])
    )

    col4.metric(
        "Total Downtime Hours",
        f"{overall_kpis['total_downtime_hours']:,.1f}"
    )

    col5, col6, col7 = st.columns(3)

    col5.metric("OEE", format_percent(overall_kpis["oee"]))
    col6.metric("Yield", format_percent(overall_kpis["yield_rate"]))
    col7.metric("UPH", f"{overall_kpis['uph']:,.1f}")

    st.divider()

    date_kpis = calculate_date_kpis(filtered_production)

    fig_oee_trend = px.line(
        date_kpis,
        x="date",
        y="oee",
        title="OEE Trend by Date",
        markers=True
    )
    fig_oee_trend.update_yaxes(tickformat=".0%")

    st.plotly_chart(
        fig_oee_trend,
        use_container_width=True,
        key="tab1_oee_trend"
    )

    col_a, col_b = st.columns(2)

    output_by_date = filtered_production.groupby(
        "date",
        as_index=False
    )[["planned_output", "actual_output"]].sum()

    fig_output = px.line(
        output_by_date,
        x="date",
        y=["planned_output", "actual_output"],
        title="Planned vs Actual Output Trend",
        markers=True
    )

    col_a.plotly_chart(
        fig_output,
        use_container_width=True,
        key="tab1_output_trend"
    )

    line_kpis = calculate_group_kpis(filtered_production, "line_id")

    fig_oee_line = px.bar(
        line_kpis,
        x="line_id",
        y="oee",
        title="OEE by Production Line",
        text_auto=".2%"
    )
    fig_oee_line.update_yaxes(tickformat=".0%")

    col_b.plotly_chart(
        fig_oee_line,
        use_container_width=True,
        key="tab1_oee_by_line"
    )

    col_c, col_d = st.columns(2)

    product_kpis = calculate_group_kpis(filtered_production, "product_type")

    fig_yield_product = px.bar(
        product_kpis,
        x="product_type",
        y="yield_rate",
        title="Yield by Product Type",
        text_auto=".2%"
    )
    fig_yield_product.update_yaxes(tickformat=".0%")

    col_c.plotly_chart(
        fig_yield_product,
        use_container_width=True,
        key="tab1_yield_by_product"
    )

    shift_kpis = calculate_group_kpis(filtered_production, "shift")

    fig_downtime_shift = px.bar(
        shift_kpis,
        x="shift",
        y="downtime_rate",
        title="Downtime Rate by Shift",
        text_auto=".2%"
    )
    fig_downtime_shift.update_yaxes(tickformat=".0%")

    col_d.plotly_chart(
        fig_downtime_shift,
        use_container_width=True,
        key="tab1_downtime_by_shift"
    )

# ============================================================
# Tab 2: OEE Loss Breakdown
# ============================================================

with tab2:
    st.header("OEE Loss Breakdown")

    st.write(
        "This section decomposes OEE into Availability, Performance, and Quality "
        "to identify whether production losses are mainly caused by downtime, "
        "speed loss, or quality loss."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("OEE", format_percent(overall_kpis["oee"]))
    col2.metric("Availability", format_percent(overall_kpis["availability"]))
    col3.metric("Performance", format_percent(overall_kpis["performance"]))
    col4.metric("Quality", format_percent(overall_kpis["quality"]))

    st.divider()

    line_kpis = calculate_group_kpis(filtered_production, "line_id")

    oee_components = line_kpis[
        ["line_id", "availability", "performance", "quality"]
    ].melt(
        id_vars="line_id",
        var_name="OEE Component",
        value_name="Value"
    )

    fig_components = px.bar(
        oee_components,
        x="line_id",
        y="Value",
        color="OEE Component",
        barmode="group",
        title="Availability, Performance and Quality by Line",
        text_auto=".2%"
    )
    fig_components.update_yaxes(tickformat=".0%")

    st.plotly_chart(
        fig_components,
        use_container_width=True,
        key="tab2_oee_components"
    )

    col_a, col_b = st.columns(2)

    machine_kpis = calculate_group_kpis(filtered_production, "machine_id")
    machine_kpis = machine_kpis.sort_values("oee", ascending=True)

    fig_machine = px.bar(
        machine_kpis,
        x="oee",
        y="machine_id",
        orientation="h",
        title="OEE by Machine",
        text_auto=".2%"
    )
    fig_machine.update_xaxes(tickformat=".0%")

    col_a.plotly_chart(
        fig_machine,
        use_container_width=True,
        key="tab2_oee_by_machine"
    )

    shift_kpis = calculate_group_kpis(filtered_production, "shift")

    fig_shift = px.bar(
        shift_kpis,
        x="shift",
        y="oee",
        title="OEE by Shift",
        text_auto=".2%"
    )
    fig_shift.update_yaxes(tickformat=".0%")

    col_b.plotly_chart(
        fig_shift,
        use_container_width=True,
        key="tab2_oee_by_shift"
    )

    date_line_records = []

    for (date_value, line_value), group_df in filtered_production.groupby(
        ["date", "line_id"]
    ):
        kpis = calculate_kpis(group_df)
        date_line_records.append({
            "date": date_value,
            "line_id": line_value,
            "oee": kpis["oee"]
        })

    date_line_kpis = pd.DataFrame(date_line_records)

    fig_oee_line_trend = px.line(
        date_line_kpis,
        x="date",
        y="oee",
        color="line_id",
        title="OEE Trend by Production Line",
        markers=True
    )
    fig_oee_line_trend.update_yaxes(tickformat=".0%")

    st.plotly_chart(
        fig_oee_line_trend,
        use_container_width=True,
        key="tab2_oee_line_trend"
    )

# ============================================================
# Tab 3: Downtime Root Cause
# ============================================================

with tab3:
    st.header("Downtime Root Cause Analysis")

    st.write(
        "This section identifies major downtime drivers by reason, machine, "
        "line, shift, and severity."
    )

    total_downtime_minutes_from_log = filtered_downtime["downtime_minutes"].sum()
    total_downtime_events = len(filtered_downtime)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Downtime Hours",
        f"{total_downtime_minutes_from_log / 60:,.1f}"
    )

    col2.metric(
        "Total Downtime Events",
        format_number(total_downtime_events)
    )

    col3.metric(
        "Downtime Rate",
        format_percent(overall_kpis["downtime_rate"])
    )

    col4.metric(
        "OEE",
        format_percent(overall_kpis["oee"])
    )

    st.divider()

    col_a, col_b = st.columns(2)

    downtime_by_reason = downtime_analysis.groupby(
        "downtime_reason",
        as_index=False
    )["downtime_minutes"].sum().sort_values(
        "downtime_minutes",
        ascending=True
    )

    fig_reason = px.bar(
        downtime_by_reason,
        x="downtime_minutes",
        y="downtime_reason",
        orientation="h",
        title="Downtime Minutes by Reason",
        text_auto=True
    )

    col_a.plotly_chart(
        fig_reason,
        use_container_width=True,
        key="tab3_downtime_by_reason"
    )

    downtime_by_machine = downtime_analysis.groupby(
        "machine_id",
        as_index=False
    )["downtime_minutes"].sum().sort_values(
        "downtime_minutes",
        ascending=True
    )

    fig_machine_down = px.bar(
        downtime_by_machine,
        x="downtime_minutes",
        y="machine_id",
        orientation="h",
        title="Downtime Minutes by Machine",
        text_auto=True
    )

    col_b.plotly_chart(
        fig_machine_down,
        use_container_width=True,
        key="tab3_downtime_by_machine"
    )

    col_c, col_d = st.columns(2)

    downtime_by_line = downtime_analysis.groupby(
        "line_id",
        as_index=False
    )["downtime_minutes"].sum()

    fig_line_down = px.bar(
        downtime_by_line,
        x="line_id",
        y="downtime_minutes",
        title="Downtime Minutes by Production Line",
        text_auto=True
    )

    col_c.plotly_chart(
        fig_line_down,
        use_container_width=True,
        key="tab3_downtime_by_line"
    )

    downtime_by_shift = downtime_analysis.groupby(
        "shift",
        as_index=False
    )["downtime_minutes"].sum()

    fig_shift_down = px.bar(
        downtime_by_shift,
        x="shift",
        y="downtime_minutes",
        title="Downtime Minutes by Shift",
        text_auto=True
    )

    col_d.plotly_chart(
        fig_shift_down,
        use_container_width=True,
        key="tab3_downtime_by_shift"
    )

    col_e, col_f = st.columns(2)

    downtime_by_severity = downtime_analysis.groupby(
        "severity",
        as_index=False
    )["downtime_minutes"].sum()

    fig_severity = px.pie(
        downtime_by_severity,
        names="severity",
        values="downtime_minutes",
        title="Downtime Minutes by Severity",
        hole=0.45
    )

    col_e.plotly_chart(
        fig_severity,
        use_container_width=True,
        key="tab3_downtime_by_severity"
    )

    downtime_by_date = downtime_analysis.groupby(
        "date",
        as_index=False
    )["downtime_minutes"].sum()

    fig_downtrend = px.line(
        downtime_by_date,
        x="date",
        y="downtime_minutes",
        title="Downtime Trend by Date",
        markers=True
    )

    col_f.plotly_chart(
        fig_downtrend,
        use_container_width=True,
        key="tab3_downtime_trend"
    )

# ============================================================
# Tab 4: Yield and Defect Analysis
# ============================================================

with tab4:
    st.header("Yield and Defect Analysis")

    st.write(
        "This section evaluates quality performance by product type, "
        "defect type, and process stage."
    )

    total_defect_count = filtered_defect["defect_count"].sum()
    total_defect_records = len(filtered_defect)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Yield", format_percent(overall_kpis["yield_rate"]))
    col2.metric("Defect Rate", format_percent(overall_kpis["defect_rate"]))
    col3.metric("Total Defect Count", format_number(total_defect_count))
    col4.metric("Total Defect Records", format_number(total_defect_records))

    st.divider()

    col_a, col_b = st.columns(2)

    product_kpis = calculate_group_kpis(filtered_production, "product_type")

    fig_yield = px.bar(
        product_kpis,
        x="product_type",
        y="yield_rate",
        title="Yield by Product Type",
        text_auto=".2%"
    )
    fig_yield.update_yaxes(tickformat=".0%")

    col_a.plotly_chart(
        fig_yield,
        use_container_width=True,
        key="tab4_yield_by_product"
    )

    fig_defect_rate = px.bar(
        product_kpis,
        x="product_type",
        y="defect_rate",
        title="Defect Rate by Product Type",
        text_auto=".2%"
    )
    fig_defect_rate.update_yaxes(tickformat=".0%")

    col_b.plotly_chart(
        fig_defect_rate,
        use_container_width=True,
        key="tab4_defect_rate_by_product"
    )

    col_c, col_d = st.columns(2)

    defect_by_type = defect_analysis.groupby(
        "defect_type",
        as_index=False
    )["defect_count"].sum().sort_values(
        "defect_count",
        ascending=True
    )

    fig_defect_type = px.bar(
        defect_by_type,
        x="defect_count",
        y="defect_type",
        orientation="h",
        title="Defect Count by Defect Type",
        text_auto=True
    )

    col_c.plotly_chart(
        fig_defect_type,
        use_container_width=True,
        key="tab4_defect_by_type"
    )

    defect_by_stage = defect_analysis.groupby(
        "process_stage",
        as_index=False
    )["defect_count"].sum().sort_values(
        "defect_count",
        ascending=False
    )

    fig_stage = px.bar(
        defect_by_stage,
        x="process_stage",
        y="defect_count",
        title="Defect Count by Process Stage",
        text_auto=True
    )

    col_d.plotly_chart(
        fig_stage,
        use_container_width=True,
        key="tab4_defect_by_stage"
    )

    defect_by_date = defect_analysis.groupby(
        "date",
        as_index=False
    )["defect_count"].sum()

    fig_defect_trend = px.line(
        defect_by_date,
        x="date",
        y="defect_count",
        title="Defect Trend by Date",
        markers=True
    )

    st.plotly_chart(
        fig_defect_trend,
        use_container_width=True,
        key="tab4_defect_trend"
    )

# ============================================================
# Tab 5: Automated Daily Report
# ============================================================

with tab5:
    st.header("Automated Daily KPI Report")

    st.write(
        "This section generates a daily manufacturing KPI report with "
        "production performance, downtime root cause, worst machine, and "
        "threshold-based alerts."
    )

    available_dates = sorted(filtered_production["date"].dt.date.unique())

    selected_report_date = st.selectbox(
        "Select Report Date",
        options=available_dates,
        index=len(available_dates) - 1
    )

    daily_production = filtered_production[
        filtered_production["date"].dt.date == selected_report_date
    ].copy()

    daily_production_ids = daily_production["production_id"].unique()

    daily_downtime = downtime_log[
        downtime_log["production_id"].isin(daily_production_ids)
    ].copy()

    daily_defect = defect_log[
        defect_log["production_id"].isin(daily_production_ids)
    ].copy()

    daily_kpis = calculate_kpis(daily_production)

    # ------------------------------------------------------------
    # Identify top downtime reason
    # ------------------------------------------------------------

    if not daily_downtime.empty:
        top_downtime_reason_df = daily_downtime.groupby(
            "downtime_reason",
            as_index=False
        )["downtime_minutes"].sum().sort_values(
            "downtime_minutes",
            ascending=False
        )

        top_downtime_reason = top_downtime_reason_df.iloc[0]["downtime_reason"]
        top_downtime_minutes = top_downtime_reason_df.iloc[0]["downtime_minutes"]
    else:
        top_downtime_reason = "No downtime recorded"
        top_downtime_minutes = 0

    # ------------------------------------------------------------
    # Identify worst machine by downtime
    # ------------------------------------------------------------

    if not daily_downtime.empty:
        worst_machine_df = daily_downtime.groupby(
            "machine_id",
            as_index=False
        )["downtime_minutes"].sum().sort_values(
            "downtime_minutes",
            ascending=False
        )

        worst_machine = worst_machine_df.iloc[0]["machine_id"]
        worst_machine_downtime = worst_machine_df.iloc[0]["downtime_minutes"]
    else:
        worst_machine = "No downtime recorded"
        worst_machine_downtime = 0

    # ------------------------------------------------------------
    # Alert logic
    # ------------------------------------------------------------

    alerts = []

    if daily_kpis["oee"] < 0.75:
        alerts.append("Low OEE Alert")

    if daily_kpis["yield_rate"] < 0.95:
        alerts.append("Quality Alert")

    if daily_kpis["downtime_rate"] > 0.15:
        alerts.append("High Downtime Alert")

    if daily_kpis["uph"] < filtered_production["uph"].mean():
        alerts.append("Below Average UPH Alert")

    if len(alerts) == 0:
        alert_status = "Normal"
    else:
        alert_status = " | ".join(alerts)

    # ------------------------------------------------------------
    # KPI Cards
    # ------------------------------------------------------------

    st.subheader(f"Daily Report Summary: {selected_report_date}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Daily Planned Output",
        format_number(daily_kpis["total_planned_output"])
    )

    col2.metric(
        "Daily Actual Output",
        format_number(daily_kpis["total_actual_output"])
    )

    col3.metric(
        "Daily Good Units",
        format_number(daily_kpis["total_good_units"])
    )

    col4.metric(
        "Daily Downtime Hours",
        f"{daily_kpis['total_downtime_hours']:,.1f}"
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("Daily OEE", format_percent(daily_kpis["oee"]))
    col6.metric("Daily Yield", format_percent(daily_kpis["yield_rate"]))
    col7.metric("Daily UPH", f"{daily_kpis['uph']:,.1f}")
    col8.metric("Downtime Rate", format_percent(daily_kpis["downtime_rate"]))

    st.divider()

    # ------------------------------------------------------------
    # Operational summary
    # ------------------------------------------------------------

    col_a, col_b, col_c = st.columns(3)

    col_a.info(
        f"Top Downtime Reason\n\n"
        f"{top_downtime_reason}\n\n"
        f"{top_downtime_minutes:,.0f} minutes"
    )

    col_b.warning(
        f"Worst Machine by Downtime\n\n"
        f"{worst_machine}\n\n"
        f"{worst_machine_downtime:,.0f} minutes"
    )

    if alert_status == "Normal":
        col_c.success(
            f"Alert Status\n\n"
            f"{alert_status}"
        )
    else:
        col_c.error(
            f"Alert Status\n\n"
            f"{alert_status}"
        )

    st.divider()

    # ------------------------------------------------------------
    # Daily report table
    # ------------------------------------------------------------

    daily_report = pd.DataFrame([{
        "report_date": selected_report_date,
        "total_planned_output": daily_kpis["total_planned_output"],
        "total_actual_output": daily_kpis["total_actual_output"],
        "total_good_units": daily_kpis["total_good_units"],
        "total_defective_units": daily_kpis["total_defective_units"],
        "total_downtime_hours": round(daily_kpis["total_downtime_hours"], 2),
        "availability": round(daily_kpis["availability"], 4),
        "performance": round(daily_kpis["performance"], 4),
        "quality": round(daily_kpis["quality"], 4),
        "oee": round(daily_kpis["oee"], 4),
        "yield_rate": round(daily_kpis["yield_rate"], 4),
        "defect_rate": round(daily_kpis["defect_rate"], 4),
        "uph": round(daily_kpis["uph"], 2),
        "downtime_rate": round(daily_kpis["downtime_rate"], 4),
        "top_downtime_reason": top_downtime_reason,
        "top_downtime_minutes": top_downtime_minutes,
        "worst_machine": worst_machine,
        "worst_machine_downtime_minutes": worst_machine_downtime,
        "alert_status": alert_status
    }])

    st.subheader("Generated Daily KPI Report")

    display_report = daily_report.copy()

    percentage_columns = [
        "availability",
        "performance",
        "quality",
        "oee",
        "yield_rate",
        "defect_rate",
        "downtime_rate"
    ]

    for col in percentage_columns:
        display_report[col] = display_report[col].apply(lambda x: f"{x * 100:.2f}%")

    st.dataframe(display_report, use_container_width=True)

    # ------------------------------------------------------------
    # Download button
    # ------------------------------------------------------------

    st.divider()

    # ------------------------------------------------------------
    # Daily visual checks
    # ------------------------------------------------------------

    st.subheader("Daily Supporting Analysis")

    col_x, col_y = st.columns(2)

    if not daily_downtime.empty:
        daily_downtime_reason = daily_downtime.groupby(
            "downtime_reason",
            as_index=False
        )["downtime_minutes"].sum().sort_values(
            "downtime_minutes",
            ascending=True
        )

        fig_daily_reason = px.bar(
            daily_downtime_reason,
            x="downtime_minutes",
            y="downtime_reason",
            orientation="h",
            title="Daily Downtime Minutes by Reason",
            text_auto=True
        )

        col_x.plotly_chart(
            fig_daily_reason,
            use_container_width=True,
            key="tab5_daily_downtime_reason"
        )
    else:
        col_x.info("No downtime records available for this date.")

    if not daily_defect.empty:
        daily_defect_type = daily_defect.groupby(
            "defect_type",
            as_index=False
        )["defect_count"].sum().sort_values(
            "defect_count",
            ascending=True
        )

        fig_daily_defect = px.bar(
            daily_defect_type,
            x="defect_count",
            y="defect_type",
            orientation="h",
            title="Daily Defect Count by Defect Type",
            text_auto=True
        )

        col_y.plotly_chart(
            fig_daily_defect,
            use_container_width=True,
            key="tab5_daily_defect_type"
        )
    else:
        col_y.info("No defect records available for this date.")


    csv_report = daily_report.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Download Daily KPI Report as CSV",
        data=csv_report,
        file_name=f"daily_kpi_report_{selected_report_date}.csv",
        mime="text/csv",
        key="tab5_download_daily_csv"
    )

    pdf_buffer = generate_daily_pdf_report(
        report_date=selected_report_date,
        daily_kpis=daily_kpis,
        top_downtime_reason=top_downtime_reason,
        top_downtime_minutes=top_downtime_minutes,
        worst_machine=worst_machine,
        worst_machine_downtime=worst_machine_downtime,
        alert_status=alert_status,
        daily_report=daily_report
    )

    st.download_button(
        label="Download Daily KPI Report as PDF",
        data=pdf_buffer.getvalue(),
        file_name=f"daily_kpi_report_{selected_report_date}.pdf",
        mime="application/pdf",
        key="tab5_download_daily_pdf"
    )
# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "Portfolio project: Smart Factory KPI Monitoring and Reporting Automation System. "
    "Built using simulated MES-style production data, Python, Streamlit, Pandas, and Plotly."
)