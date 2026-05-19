-- ============================================================
-- Smart Factory KPI Monitoring and Reporting Automation System
-- SQL Analysis Layer
-- Database style: SQLite-compatible SQL
-- Author: Portfolio Project
-- ============================================================

-- ------------------------------------------------------------
-- 0. Expected Tables
-- ------------------------------------------------------------
-- Production_Log
-- Downtime_Log
-- Machine_Master
-- Defect_Log

-- ------------------------------------------------------------
-- 1. Production KPI View
-- Purpose: Recalculate manufacturing KPIs from raw production fields.
-- ------------------------------------------------------------

DROP VIEW IF EXISTS vw_production_kpi;

CREATE VIEW vw_production_kpi AS
SELECT
    production_id,
    date,
    shift,
    line_id,
    machine_id,
    product_type,
    planned_output,
    actual_output,
    good_units,
    defective_units,
    planned_production_minutes,
    downtime_minutes,
    operating_minutes,
    operating_hours,

    CASE
        WHEN planned_production_minutes = 0 THEN NULL
        ELSE 1.0 * operating_minutes / planned_production_minutes
    END AS availability,

    CASE
        WHEN planned_output = 0 THEN NULL
        ELSE 1.0 * actual_output / planned_output
    END AS performance,

    CASE
        WHEN actual_output = 0 THEN NULL
        ELSE 1.0 * good_units / actual_output
    END AS quality,

    CASE
        WHEN planned_production_minutes = 0 OR planned_output = 0 OR actual_output = 0 THEN NULL
        ELSE
            (1.0 * operating_minutes / planned_production_minutes) *
            (1.0 * actual_output / planned_output) *
            (1.0 * good_units / actual_output)
    END AS oee,

    CASE
        WHEN actual_output = 0 THEN NULL
        ELSE 1.0 * good_units / actual_output
    END AS yield_rate,

    CASE
        WHEN actual_output = 0 THEN NULL
        ELSE 1.0 * defective_units / actual_output
    END AS defect_rate,

    CASE
        WHEN operating_hours = 0 THEN NULL
        ELSE 1.0 * actual_output / operating_hours
    END AS uph,

    CASE
        WHEN planned_production_minutes = 0 THEN NULL
        ELSE 1.0 * downtime_minutes / planned_production_minutes
    END AS downtime_rate
FROM Production_Log;

-- ------------------------------------------------------------
-- 2. Overall Factory KPI Summary
-- Purpose: One-row factory-level KPI summary.
-- ------------------------------------------------------------

SELECT
    SUM(planned_output) AS total_planned_output,
    SUM(actual_output) AS total_actual_output,
    SUM(good_units) AS total_good_units,
    SUM(defective_units) AS total_defective_units,
    ROUND(SUM(downtime_minutes) / 60.0, 2) AS total_downtime_hours,
    ROUND(1.0 * SUM(operating_minutes) / SUM(planned_production_minutes), 4) AS availability,
    ROUND(1.0 * SUM(actual_output) / SUM(planned_output), 4) AS performance,
    ROUND(1.0 * SUM(good_units) / SUM(actual_output), 4) AS quality,
    ROUND(
        (1.0 * SUM(operating_minutes) / SUM(planned_production_minutes)) *
        (1.0 * SUM(actual_output) / SUM(planned_output)) *
        (1.0 * SUM(good_units) / SUM(actual_output)),
        4
    ) AS oee,
    ROUND(1.0 * SUM(good_units) / SUM(actual_output), 4) AS yield_rate,
    ROUND(1.0 * SUM(defective_units) / SUM(actual_output), 4) AS defect_rate,
    ROUND(1.0 * SUM(actual_output) / SUM(operating_hours), 2) AS uph,
    ROUND(1.0 * SUM(downtime_minutes) / SUM(planned_production_minutes), 4) AS downtime_rate
FROM Production_Log;

-- ------------------------------------------------------------
-- 3. Daily Production Summary
-- Purpose: Daily output and KPI monitoring.
-- ------------------------------------------------------------

SELECT
    date,
    SUM(planned_output) AS planned_output,
    SUM(actual_output) AS actual_output,
    SUM(good_units) AS good_units,
    SUM(defective_units) AS defective_units,
    ROUND(SUM(downtime_minutes) / 60.0, 2) AS downtime_hours,
    ROUND(1.0 * SUM(operating_minutes) / SUM(planned_production_minutes), 4) AS availability,
    ROUND(1.0 * SUM(actual_output) / SUM(planned_output), 4) AS performance,
    ROUND(1.0 * SUM(good_units) / SUM(actual_output), 4) AS quality,
    ROUND(
        (1.0 * SUM(operating_minutes) / SUM(planned_production_minutes)) *
        (1.0 * SUM(actual_output) / SUM(planned_output)) *
        (1.0 * SUM(good_units) / SUM(actual_output)),
        4
    ) AS oee,
    ROUND(1.0 * SUM(good_units) / SUM(actual_output), 4) AS yield_rate,
    ROUND(1.0 * SUM(actual_output) / SUM(operating_hours), 2) AS uph,
    ROUND(1.0 * SUM(downtime_minutes) / SUM(planned_production_minutes), 4) AS downtime_rate
FROM Production_Log
GROUP BY date
ORDER BY date;

-- ------------------------------------------------------------
-- 4. OEE by Production Line
-- Purpose: Identify the weakest and strongest lines.
-- ------------------------------------------------------------

SELECT
    line_id,
    SUM(planned_output) AS planned_output,
    SUM(actual_output) AS actual_output,
    ROUND(SUM(downtime_minutes) / 60.0, 2) AS downtime_hours,
    ROUND(1.0 * SUM(operating_minutes) / SUM(planned_production_minutes), 4) AS availability,
    ROUND(1.0 * SUM(actual_output) / SUM(planned_output), 4) AS performance,
    ROUND(1.0 * SUM(good_units) / SUM(actual_output), 4) AS quality,
    ROUND(
        (1.0 * SUM(operating_minutes) / SUM(planned_production_minutes)) *
        (1.0 * SUM(actual_output) / SUM(planned_output)) *
        (1.0 * SUM(good_units) / SUM(actual_output)),
        4
    ) AS oee
FROM Production_Log
GROUP BY line_id
ORDER BY oee ASC;

-- ------------------------------------------------------------
-- 5. OEE by Machine
-- Purpose: Identify low-performing machines.
-- ------------------------------------------------------------

SELECT
    p.machine_id,
    m.line_id,
    m.machine_type,
    SUM(p.planned_output) AS planned_output,
    SUM(p.actual_output) AS actual_output,
    ROUND(SUM(p.downtime_minutes) / 60.0, 2) AS downtime_hours,
    ROUND(
        (1.0 * SUM(p.operating_minutes) / SUM(p.planned_production_minutes)) *
        (1.0 * SUM(p.actual_output) / SUM(p.planned_output)) *
        (1.0 * SUM(p.good_units) / SUM(p.actual_output)),
        4
    ) AS oee,
    ROUND(1.0 * SUM(p.actual_output) / SUM(p.operating_hours), 2) AS uph,
    m.standard_uph,
    ROUND(1.0 * SUM(p.actual_output) / SUM(p.operating_hours) - m.standard_uph, 2) AS uph_gap
FROM Production_Log p
LEFT JOIN Machine_Master m
    ON p.machine_id = m.machine_id
GROUP BY p.machine_id, m.line_id, m.machine_type, m.standard_uph
ORDER BY oee ASC;

-- ------------------------------------------------------------
-- 6. Downtime by Reason
-- Purpose: Root cause analysis for availability loss.
-- ------------------------------------------------------------

SELECT
    downtime_reason,
    COUNT(*) AS downtime_events,
    SUM(downtime_minutes) AS total_downtime_minutes,
    ROUND(SUM(downtime_minutes) / 60.0, 2) AS total_downtime_hours,
    ROUND(
        1.0 * SUM(downtime_minutes) /
        (SELECT SUM(downtime_minutes) FROM Downtime_Log),
        4
    ) AS downtime_contribution
FROM Downtime_Log
GROUP BY downtime_reason
ORDER BY total_downtime_minutes DESC;

-- ------------------------------------------------------------
-- 7. Worst 5 Machines by Downtime
-- Purpose: Identify priority machines for maintenance or review.
-- ------------------------------------------------------------

SELECT
    d.machine_id,
    m.line_id,
    m.machine_type,
    COUNT(*) AS downtime_events,
    SUM(d.downtime_minutes) AS total_downtime_minutes,
    ROUND(SUM(d.downtime_minutes) / 60.0, 2) AS total_downtime_hours
FROM Downtime_Log d
LEFT JOIN Machine_Master m
    ON d.machine_id = m.machine_id
GROUP BY d.machine_id, m.line_id, m.machine_type
ORDER BY total_downtime_minutes DESC
LIMIT 5;

-- ------------------------------------------------------------
-- 8. Downtime by Line and Shift
-- Purpose: Identify whether downtime is concentrated by line or shift.
-- ------------------------------------------------------------

SELECT
    p.line_id,
    p.shift,
    SUM(d.downtime_minutes) AS total_downtime_minutes,
    ROUND(SUM(d.downtime_minutes) / 60.0, 2) AS total_downtime_hours,
    COUNT(d.downtime_id) AS downtime_events
FROM Downtime_Log d
LEFT JOIN Production_Log p
    ON d.production_id = p.production_id
GROUP BY p.line_id, p.shift
ORDER BY total_downtime_minutes DESC;

-- ------------------------------------------------------------
-- 9. Defect Count by Product Type
-- Purpose: Identify product types with higher defect burden.
-- ------------------------------------------------------------

SELECT
    product_type,
    SUM(defect_count) AS total_defect_count,
    COUNT(*) AS defect_records,
    ROUND(
        1.0 * SUM(defect_count) /
        (SELECT SUM(defect_count) FROM Defect_Log),
        4
    ) AS defect_contribution
FROM Defect_Log
GROUP BY product_type
ORDER BY total_defect_count DESC;

-- ------------------------------------------------------------
-- 10. Defect Count by Defect Type
-- Purpose: Quality root cause analysis.
-- ------------------------------------------------------------

SELECT
    defect_type,
    SUM(defect_count) AS total_defect_count,
    COUNT(*) AS defect_records,
    ROUND(
        1.0 * SUM(defect_count) /
        (SELECT SUM(defect_count) FROM Defect_Log),
        4
    ) AS defect_contribution
FROM Defect_Log
GROUP BY defect_type
ORDER BY total_defect_count DESC;

-- ------------------------------------------------------------
-- 11. Defect Count by Process Stage
-- Purpose: Identify process stages with higher quality risk.
-- ------------------------------------------------------------

SELECT
    process_stage,
    SUM(defect_count) AS total_defect_count,
    COUNT(*) AS defect_records,
    ROUND(
        1.0 * SUM(defect_count) /
        (SELECT SUM(defect_count) FROM Defect_Log),
        4
    ) AS defect_contribution
FROM Defect_Log
GROUP BY process_stage
ORDER BY total_defect_count DESC;

-- ------------------------------------------------------------
-- 12. Yield by Product Type
-- Purpose: Compare quality performance across product types.
-- ------------------------------------------------------------

SELECT
    product_type,
    SUM(actual_output) AS actual_output,
    SUM(good_units) AS good_units,
    SUM(defective_units) AS defective_units,
    ROUND(1.0 * SUM(good_units) / SUM(actual_output), 4) AS yield_rate,
    ROUND(1.0 * SUM(defective_units) / SUM(actual_output), 4) AS defect_rate
FROM Production_Log
GROUP BY product_type
ORDER BY yield_rate ASC;

-- ------------------------------------------------------------
-- 13. Yield by Shift
-- Purpose: Check whether quality differs between day and night shift.
-- ------------------------------------------------------------

SELECT
    shift,
    SUM(actual_output) AS actual_output,
    SUM(good_units) AS good_units,
    SUM(defective_units) AS defective_units,
    ROUND(1.0 * SUM(good_units) / SUM(actual_output), 4) AS yield_rate,
    ROUND(1.0 * SUM(defective_units) / SUM(actual_output), 4) AS defect_rate
FROM Production_Log
GROUP BY shift
ORDER BY yield_rate ASC;

-- ------------------------------------------------------------
-- 14. Monthly Production Trend
-- Purpose: Monthly output and performance monitoring.
-- SQLite uses substr(date, 1, 7) to extract YYYY-MM if date is stored as text.
-- ------------------------------------------------------------

SELECT
    substr(date, 1, 7) AS production_month,
    SUM(planned_output) AS planned_output,
    SUM(actual_output) AS actual_output,
    SUM(good_units) AS good_units,
    ROUND(SUM(downtime_minutes) / 60.0, 2) AS downtime_hours,
    ROUND(1.0 * SUM(good_units) / SUM(actual_output), 4) AS yield_rate,
    ROUND(
        (1.0 * SUM(operating_minutes) / SUM(planned_production_minutes)) *
        (1.0 * SUM(actual_output) / SUM(planned_output)) *
        (1.0 * SUM(good_units) / SUM(actual_output)),
        4
    ) AS oee
FROM Production_Log
GROUP BY substr(date, 1, 7)
ORDER BY production_month;

-- ------------------------------------------------------------
-- 15. High-Risk Production Records
-- Purpose: Flag records that need operational review.
-- ------------------------------------------------------------

SELECT
    production_id,
    date,
    shift,
    line_id,
    machine_id,
    product_type,
    planned_output,
    actual_output,
    good_units,
    defective_units,
    downtime_minutes,
    ROUND(1.0 * good_units / actual_output, 4) AS yield_rate,
    ROUND(1.0 * downtime_minutes / planned_production_minutes, 4) AS downtime_rate,
    CASE
        WHEN actual_output < planned_output * 0.80 THEN 'Low Output'
        WHEN 1.0 * good_units / actual_output < 0.95 THEN 'Low Yield'
        WHEN 1.0 * downtime_minutes / planned_production_minutes > 0.15 THEN 'High Downtime'
        ELSE 'Normal'
    END AS risk_flag
FROM Production_Log
WHERE
    actual_output < planned_output * 0.80
    OR 1.0 * good_units / actual_output < 0.95
    OR 1.0 * downtime_minutes / planned_production_minutes > 0.15
ORDER BY date, line_id, machine_id;

-- ------------------------------------------------------------
-- 16. Data Quality Validation Checks
-- Purpose: Detect data issues before KPI calculation.
-- ------------------------------------------------------------

SELECT
    'Duplicate production_id' AS validation_rule,
    COUNT(*) AS failed_records
FROM (
    SELECT production_id
    FROM Production_Log
    GROUP BY production_id
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'Unit mismatch: good_units + defective_units != actual_output' AS validation_rule,
    COUNT(*) AS failed_records
FROM Production_Log
WHERE good_units + defective_units != actual_output

UNION ALL

SELECT
    'Downtime exceeds planned production time' AS validation_rule,
    COUNT(*) AS failed_records
FROM Production_Log
WHERE downtime_minutes > planned_production_minutes

UNION ALL

SELECT
    'Negative production values' AS validation_rule,
    COUNT(*) AS failed_records
FROM Production_Log
WHERE planned_output < 0
   OR actual_output < 0
   OR good_units < 0
   OR defective_units < 0
   OR downtime_minutes < 0;
