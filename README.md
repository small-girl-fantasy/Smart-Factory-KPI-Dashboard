# Smart Factory KPI Monitoring and Reporting Automation System

## Live Demo

[Open the Streamlit Dashboard]([https://smart-factory-kpi-dashboard-xo9befc2kgyh38jqtwxrtb.streamlit.app/)

## 1. Project Overview

This project is a simulated smart factory analytics and reporting automation system designed to monitor manufacturing performance using MES-style production data.

The system tracks key manufacturing KPIs including OEE, Availability, Performance, Quality, Yield, UPH, Downtime Rate, Defect Rate, downtime reasons, machine-level losses, and defect patterns.

The project includes two dashboard versions:

- **Power BI Dashboard**: a business intelligence reporting version for manufacturing KPI monitoring.
- **Streamlit Dashboard**: a Python-based interactive web application with automated daily KPI reporting and downloadable CSV/PDF reports.

This project was developed to demonstrate practical skills in manufacturing analytics, business intelligence, data validation, KPI monitoring, reporting automation, and factory digital transformation.

---

## 2. Business Problem

Manufacturing teams need timely and reliable visibility into production performance. However, production data is often stored across multiple systems such as MES logs, downtime records, machine master data, and defect records.

Without a structured analytics system, it is difficult to identify whether production losses are caused by downtime, low speed, quality issues, specific machines, specific shifts, or specific product types.

This project addresses the following business questions:

- Is the factory meeting planned production targets?
- Which production line has the weakest OEE performance?
- Is OEE loss mainly driven by Availability, Performance, or Quality?
- Which downtime reasons contribute most to production loss?
- Which machines have the highest downtime?
- Which products have lower yield or higher defect rates?
- Can daily manufacturing KPI reports be automatically generated for operational monitoring?

---

## 3. Dataset Description

The dataset is simulated to represent a MES-style manufacturing environment. It contains four main tables.

### 3.1 Production_Log

This is the main production fact table.

| Field | Description |
|---|---|
| production_id | Unique production record ID |
| date | Production date |
| shift | Day or Night shift |
| line_id | Production line |
| machine_id | Machine ID |
| product_type | Product category |
| planned_output | Planned production output |
| actual_output | Actual production output |
| good_units | Number of good units |
| defective_units | Number of defective units |
| planned_production_minutes | Planned production time |
| downtime_minutes | Downtime duration |
| operating_minutes | Actual operating time |
| operating_hours | Actual operating hours |
| availability | Availability KPI |
| performance | Performance KPI |
| quality | Quality KPI |
| oee | Overall Equipment Effectiveness |
| yield | Production yield |
| defect_rate | Defect rate |
| uph | Units per hour |
| downtime_rate | Downtime rate |
| data_quality_status | Data validation status |

### 3.2 Downtime_Log

This table records downtime events.

| Field | Description |
|---|---|
| downtime_id | Unique downtime event ID |
| production_id | Related production record |
| machine_id | Machine involved |
| downtime_reason | Reason for downtime |
| downtime_minutes | Downtime duration |
| severity | Low, Medium, or High severity |

### 3.3 Machine_Master

This table contains machine-level master data.

| Field | Description |
|---|---|
| machine_id | Machine ID |
| line_id | Production line |
| machine_type | Machine category |
| ideal_cycle_time_sec | Ideal cycle time |
| standard_uph | Standard units per hour |
| installation_year | Machine installation year |

### 3.4 Defect_Log

This table records product defect events.

| Field | Description |
|---|---|
| defect_id | Unique defect record ID |
| production_id | Related production record |
| product_type | Product category |
| defect_type | Type of defect |
| defect_count | Number of defects |
| process_stage | Process stage where defect occurred |

---

## 4. Data Model

The project uses a star-schema-style relationship structure.

```text
Machine_Master
      |
      | machine_id
      |
Production_Log
   /          \
  /            \
Downtime_Log   Defect_Log
```

### Relationships

| Relationship | Cardinality |
|---|---|
| Machine_Master[machine_id] → Production_Log[machine_id] | One-to-many |
| Production_Log[production_id] → Downtime_Log[production_id] | One-to-many |
| Production_Log[production_id] → Defect_Log[production_id] | One-to-many |

---

## 5. KPI Definitions

### 5.1 Availability

Availability measures the proportion of planned production time that was actually available for operation.

```text
Availability = Operating Time / Planned Production Time
```

### 5.2 Performance

Performance measures whether the factory produced close to the planned output level.

```text
Performance = Actual Output / Planned Output
```

### 5.3 Quality

Quality measures the proportion of actual output that was good output.

```text
Quality = Good Units / Actual Output
```

### 5.4 OEE

OEE measures overall equipment effectiveness by combining Availability, Performance, and Quality.

```text
OEE = Availability × Performance × Quality
```

### 5.5 Yield

Yield measures the proportion of actual production that meets quality standards.

```text
Yield = Good Units / Actual Output
```

### 5.6 Defect Rate

Defect Rate measures the proportion of defective units in total actual output.

```text
Defect Rate = Defective Units / Actual Output
```

### 5.7 UPH

UPH measures production output per operating hour.

```text
UPH = Actual Output / Operating Hours
```

### 5.8 Downtime Rate

Downtime Rate measures how much planned production time was lost due to downtime.

```text
Downtime Rate = Downtime Minutes / Planned Production Minutes
```

---

## 6. Tools and Technologies

| Tool | Purpose |
|---|---|
| Python | Data generation, data processing, automation |
| Pandas | Data manipulation and KPI calculation |
| Power BI | Business intelligence dashboard |
| DAX | KPI measure calculation in Power BI |
| Streamlit | Interactive web dashboard |
| Plotly | Interactive charts |
| ReportLab | PDF report generation |
| Excel | Data storage and inspection |
| GitHub | Project documentation and version control |

---

## 7. Project Components

### 7.1 Simulated MES Dataset

The dataset simulates production data across multiple production lines, machines, shifts, and product types. It includes production records, downtime events, machine master data, and defect records.

### 7.2 Power BI Dashboard

The Power BI dashboard provides a business intelligence reporting version of the project.

Main pages:

1. Factory Performance Overview
2. OEE Loss Breakdown
3. Downtime Root Cause Analysis
4. Yield and Defect Analysis

### 7.3 Streamlit Dashboard

The Streamlit dashboard provides a Python-based interactive analytics application.

Main tabs:

1. Factory Overview
2. OEE Loss Breakdown
3. Downtime Root Cause
4. Yield and Defect Analysis
5. Automated Daily Report

### 7.4 Automated Daily Report

The automated daily report module allows the user to select a production date and automatically generate a daily KPI summary.

The report includes:

- Daily planned output
- Daily actual output
- Daily good units
- Daily downtime hours
- Daily OEE
- Daily yield
- Daily UPH
- Downtime rate
- Top downtime reason
- Worst machine by downtime
- Alert status
- Downloadable CSV report
- Downloadable PDF report

---

## 8. Dashboard Features

### 8.1 Factory Overview

This page provides a high-level summary of factory performance.

Main visuals:

- Total Planned Output
- Total Actual Output
- Total Good Units
- Total Downtime Hours
- OEE
- Yield
- UPH
- OEE Trend by Date
- Planned vs Actual Output Trend
- OEE by Production Line
- Yield by Product Type
- Downtime Rate by Shift

### 8.2 OEE Loss Breakdown

This page decomposes OEE into Availability, Performance, and Quality.

Main visuals:

- OEE
- Availability
- Performance
- Quality
- Availability, Performance, and Quality by Line
- OEE by Machine
- OEE by Shift
- OEE Trend by Production Line

This page helps identify whether production loss is mainly caused by downtime, production speed, or quality loss.

### 8.3 Downtime Root Cause Analysis

This page identifies major downtime drivers.

Main visuals:

- Total Downtime Hours
- Total Downtime Events
- Downtime Rate
- Downtime Minutes by Reason
- Downtime Minutes by Machine
- Downtime Minutes by Production Line
- Downtime Minutes by Shift
- Downtime Minutes by Severity
- Downtime Trend by Date

This page supports root cause analysis and continuous improvement prioritization.

### 8.4 Yield and Defect Analysis

This page evaluates quality performance.

Main visuals:

- Yield
- Defect Rate
- Total Defect Count
- Total Defect Records
- Yield by Product Type
- Defect Rate by Product Type
- Defect Count by Defect Type
- Defect Count by Process Stage
- Defect Trend by Date

This page helps identify whether quality issues are concentrated in specific products, defect types, or process stages.

### 8.5 Automated Daily Report

This page generates a daily manufacturing KPI report.

Main features:

- Select report date
- Generate daily production summary
- Identify top downtime reason
- Identify worst machine by downtime
- Trigger threshold-based alerts
- Download report as CSV
- Download report as PDF

---

## 9. Alert Logic

The automated report uses simple threshold-based alert rules.

| Condition | Alert |
|---|---|
| OEE < 75% | Low OEE Alert |
| Yield < 95% | Quality Alert |
| Downtime Rate > 15% | High Downtime Alert |
| UPH below average | Below Average UPH Alert |

If no alert condition is triggered, the report status is shown as:

```text
Normal
```

---

## 10. Key Insights Supported by the Dashboard

The dashboard is designed to support the following types of insights:

1. OEE loss can be decomposed into Availability, Performance, and Quality to identify the main source of production loss.
2. A lower Availability value usually indicates downtime-related losses.
3. A lower Performance value may suggest production speed loss or output efficiency issues.
4. A lower Quality value may indicate higher defect levels or process quality issues.
5. Downtime reason analysis helps identify whether machine error, material shortage, setup changeover, maintenance, or inspection hold is the main production constraint.
6. Machine-level downtime analysis helps identify equipment that may require maintenance or operational review.
7. Defect analysis helps identify product types and process stages with higher quality risk.
8. Automated reporting improves daily production monitoring and supports faster operational decision-making.

---

## 11. How to Run the Streamlit App

### 11.1 Install Required Packages

```bash
pip install -r requirements.txt
```

### 11.2 Run the App

```bash
streamlit run streamlit_app.py
```

### 11.3 Required Files

Make sure the following files are in the same project folder:

```text
streamlit_app.py
smart_factory_mes_dataset.xlsx
requirements.txt
```

---

## 12. Project Folder Structure

Recommended folder structure:

```text
Smart-Factory-KPI-Dashboard
│
├── data
│   └── smart_factory_mes_dataset.xlsx
│
├── streamlit_app.py
├── requirements.txt
├── README.md
│
├── screenshots
│   ├── streamlit_overview.png
│   ├── streamlit_oee_breakdown.png
│   ├── streamlit_downtime_root_cause.png
│   ├── streamlit_yield_defect.png
│   ├── streamlit_daily_report.png
│   └── daily_pdf_report.png
│
└── reports
    └── sample_daily_kpi_report.pdf
```

If the Excel file is placed inside the `data` folder, the file path in `streamlit_app.py` should be updated accordingly.

---

## 13. Screenshots and Report Previews

### Factory Overview

[View Factory Overview PDF](screenshots/streamlit_overview.pdf)

### OEE Loss Breakdown

[View OEE Loss Breakdown PDF](screenshots/streamlit_oee_breakdown.pdf)

### Downtime Root Cause Analysis

[View Downtime Root Cause Analysis PDF](screenshots/streamlit_downtime_root_cause.pdf)

### Yield and Defect Analysis

[View Yield and Defect Analysis PDF](screenshots/streamlit_yield_defect.pdf)

### Automated Daily Report

[View Automated Daily Report PDF](screenshots/streamlit_daily_report.pdf)

### Sample PDF Report

[View Sample Daily KPI Report](reports/sample_daily_kpi_report.pdf)

---

## 14. Skills Demonstrated

This project demonstrates the following skills:

- Manufacturing KPI analysis
- OEE, Yield, UPH, Downtime, and Defect Rate calculation
- MES-style data modeling
- Data cleaning and validation logic
- Power BI dashboard development
- DAX measure creation
- Python dashboard development
- Streamlit web app development
- Plotly interactive visualization
- Automated reporting
- CSV and PDF report generation
- Business insight generation
- Root cause analysis
- Factory digital transformation thinking

---

## 15. Portfolio Positioning

This project is positioned as a manufacturing analytics and digital transformation portfolio project. It is especially relevant for roles such as:

- Business Operations Data Analyst
- Manufacturing Data Analyst
- BI Analyst
- Digital Operations Analyst
- Supply Chain Data Analyst
- Factory Automation Analyst
- Reporting Automation Analyst
- Industrial Data Analyst

---

## 16. CV Bullet Points

- Developed a smart factory KPI monitoring and reporting automation system using simulated MES-style production data to track OEE, yield, UPH, downtime, defect rate, and production output across production lines, machines, shifts, and product types.
- Designed a multi-table manufacturing data model including production logs, downtime records, machine master data, and defect logs to simulate factory operations data flow.
- Built an interactive Streamlit dashboard with automated daily KPI reporting, threshold-based alerts, worst-machine identification, downtime root cause analysis, and downloadable CSV/PDF reports for manufacturing operations monitoring.
- Created a Power BI dashboard to analyze factory performance, OEE loss breakdown, downtime root causes, and yield/defect patterns.
- Applied data validation logic to detect inconsistent production records, invalid downtime values, duplicated IDs, and mismatched good/defective unit totals before KPI calculation.
- Translated manufacturing analytics results into operational insights for production visibility, downtime reduction, quality monitoring, and continuous improvement decision support.

---

## 17. Limitations

This project uses simulated data rather than real factory production data. Therefore, the numerical findings should be interpreted as demonstration results rather than actual factory performance conclusions.

The project focuses on dashboarding, KPI monitoring, and reporting automation. It does not currently include predictive maintenance, advanced machine learning, or real-time IoT data streaming.

---

## 18. Future Improvements

Future improvements may include:

- Adding SQL-based data extraction and analysis queries
- Deploying the Streamlit app on Streamlit Community Cloud
- Adding a data quality validation report
- Adding a semiconductor-specific lot, wafer, test, and bin yield analysis module
- Adding predictive maintenance indicators
- Connecting the dashboard to a cloud database
- Adding user authentication
- Adding automated email report delivery
- Adding monthly management summary reports

---

## 19. Project Status

Current status:

```text
Completed initial version
```

Completed components:

- Simulated MES-style dataset
- Power BI dashboard
- Streamlit dashboard
- Automated daily KPI report
- CSV report download
- PDF report download
- README documentation
