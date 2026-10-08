import logging
import random
import pyodbc
import pandas as pd
import json
from datetime import datetime, timezone
import azure.functions as func

app = func.FunctionApp()

# Database connection string
CONN_STR = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:josephserver.database.windows.net,1433;"
    "Database=coursework2db;"
    "Uid=joe123;"
    "Pwd=Abr70Sus72;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

@app.timer_trigger(schedule="*/10 * * * * *", arg_name="myTimer", run_on_startup=False)
def insert_data(myTimer: func.TimerRequest) -> None:
    """Automatically inserts 20 simulated sensor readings every 10 seconds using a timer trigger."""

    if myTimer.past_due:
        logging.warning("Timer execution is past due!")

    logging.info("Simulated Data Timer Trigger activated.")

    # Try to connect to SQL database
    try:
        conn = pyodbc.connect(CONN_STR)
        logging.info("Database connection successful.")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return func.HttpResponse(
            f"Database connection failed: {e}",
            status_code=500
        )

    try:
        cursor = conn.cursor()

        for sensor_id in range(1, 21):
            temperature = round(random.uniform(5, 18), 2)
            wind = round(random.uniform(12, 24), 2)
            humidity = round(random.uniform(30, 60), 2)
            co2 = round(random.uniform(400, 1600), 2)

            cursor.execute("""
                INSERT INTO SensorData (sensor_id, temperature, wind, relative_humidity, co2)
                VALUES (?, ?, ?, ?, ?)
            """, (sensor_id, temperature, wind, humidity, co2))

        conn.commit()
        logging.info("Inserted 20 simulated sensor readings into SensorData.")

    except Exception as e:
        logging.error(f"Error inserting simulated readings: {e}")

# SQL configuration
@app.sql_trigger(
    arg_name="changes",
    table_name="[dbo].[SensorData]",
    connection_string_setting="SqlConnectionString"
)
def get_stats(changes: str) -> None:
    """Triggered whenever SensorData table changes. Logs each sensors statistics."""

    logging.info("SQL Trigger detected database changes.")

    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        logging.info("Database connection successful for statistics.")

        cursor.execute("""
            SELECT
                sensor_id,
                MIN(temperature)                      AS MinTemp,
                MAX(temperature)                      AS MaxTemp,
                AVG(CAST(temperature AS float))       AS AvgTemp,
                MIN(wind)                             AS MinWind,
                MAX(wind)                             AS MaxWind,
                AVG(CAST(wind AS float))              AS AvgWind,
                MIN(relative_humidity)                AS MinRH,
                MAX(relative_humidity)                AS MaxRH,
                AVG(CAST(relative_humidity AS float)) AS AvgRH,
                MIN(co2)                              AS MinCO2,
                MAX(co2)                              AS MaxCO2,
                AVG(CAST(co2 AS float))               AS AvgCO2
            FROM dbo.SensorData
            GROUP BY sensor_id
        """)

        rows = cursor.fetchall()

        if not rows:
            logging.warning("Statistics query returned no results.")
            return

        # Log sensor statistics
        for (
            sensor_id, minT, maxT, avgT, minW, maxW, avgW,
            minRH, maxRH, avgRH, minCO2, maxCO2, avgCO2
        ) in rows:

            logging.info(
                "Sensor %s | "
                "Temp(min=%s, max=%s, avg=%.2f) | "
                "Wind(min=%s, max=%s, avg=%.2f) | "
                "Humidity(min=%s, max=%s, avg=%.2f) | "
                "CO2(min=%s, max=%s, avg=%.2f)",
                sensor_id,
                minT, maxT, float(avgT or 0.0),
                minW, maxW, float(avgW or 0.0),
                minRH, maxRH, float(avgRH or 0.0),
                minCO2, maxCO2, float(avgCO2 or 0.0)
            )

    except Exception as e:
        logging.error(f"Error calculating or logging statistics: {e}")
        logging.error(f"Trigger payload: {changes}")