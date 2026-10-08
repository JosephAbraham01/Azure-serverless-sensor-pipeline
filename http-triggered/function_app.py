import logging
import random
import pyodbc
import json
import azure.functions as func

app = func.FunctionApp()

conn_str = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:josephserver.database.windows.net,1433;Database=coursework2db;Uid=joe123;Pwd=Abr70Sus72;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

@app.route(route="insert-data", methods=["POST"])
def insert_data(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP POST trigger that inserts simulated IoT sensor data into SensorData table.
    Example: POST https://<your-func>.azurewebsites.net/api/insert-data
    """
    logging.info("HTTP trigger for inserting simulated data invoked.")

    try:
        # Optional: read number of sensors or samples from body
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        sensor_count = int(req_body.get("count", 20))  # default 20 sensors
        if sensor_count < 1 or sensor_count > 1000:
            return func.HttpResponse(
                "Invalid sensor count (must be 1–1000).", status_code=400
            )

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.fast_executemany = True  # faster inserts

            for sensor_id in range(1, sensor_count + 1):
                temperature = round(random.uniform(5, 18), 2)
                wind = round(random.uniform(12, 24), 2)
                humidity = round(random.uniform(30, 60), 2)
                co2 = round(random.uniform(400, 1600), 2)

                cursor.execute(
                    """
                    INSERT INTO dbo.SensorData (sensor_id, temperature, wind, relative_humidity, co2)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (sensor_id, temperature, wind, humidity, co2),
                )

            conn.commit()
            logging.info(f"Inserted {sensor_count} simulated sensor readings.")
            return func.HttpResponse(
                f"Inserted {sensor_count} simulated sensor readings.",
                status_code=200,
            )

    except pyodbc.Error as db_err:
        logging.error(f"Database error: {db_err}")
        return func.HttpResponse(f"Database error: {db_err}", status_code=500)
    except Exception as e:
        logging.error(f"Error inserting data: {e}")
        return func.HttpResponse(f"Error inserting data: {e}", status_code=500)


@app.sql_trigger(
    arg_name="changes",
    table_name="[dbo].[SensorData]",
    connection_string_setting="SqlConnectionString",
)
def get_stats(changes: str) -> None:
    """
    SQL trigger — fires automatically when SensorData changes.
    Computes min, max, and average for each sensor and logs results.
    """
    logging.info("SQL trigger function detected changes to SensorData.")

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    sensor_id,
                    MIN(temperature) AS MinTemp,
                    MAX(temperature) AS MaxTemp,
                    AVG(CAST(temperature AS float)) AS AvgTemp,
                    MIN(wind) AS MinWind,
                    MAX(wind) AS MaxWind,
                    AVG(CAST(wind AS float)) AS AvgWind,
                    MIN(relative_humidity) AS MinRH,
                    MAX(relative_humidity) AS MaxRH,
                    AVG(CAST(relative_humidity AS float)) AS AvgRH,
                    MIN(co2) AS MinCO2,
                    MAX(co2) AS MaxCO2,
                    AVG(CAST(co2 AS float)) AS AvgCO2
                FROM dbo.SensorData
                GROUP BY sensor_id
                ORDER BY sensor_id;
                """
            )

            rows = cursor.fetchall()
            for row in rows:
                (
                    sensor_id,
                    minT, maxT, avgT,
                    minW, maxW, avgW,
                    minRH, maxRH, avgRH,
                    minCO2, maxCO2, avgCO2,
                ) = row

                logging.info(
                    "Sensor %s | Temp(min=%s, max=%s, avg=%.2f) | "
                    "Wind(min=%s, max=%s, avg=%.2f) | "
                    "Humidity(min=%s, max=%s, avg=%.2f) | "
                    "CO2(min=%s, max=%s, avg=%.2f)",
                    sensor_id,
                    minT, maxT, float(avgT or 0.0),
                    minW, maxW, float(avgW or 0.0),
                    minRH, maxRH, float(avgRH or 0.0),
                    minCO2, maxCO2, float(avgCO2 or 0.0),
                )

    except json.JSONDecodeError:
        logging.error(f"Failed to parse changes as JSON: {changes}")
    except Exception as e:
        logging.error(f"Error processing changes: {str(e)}")
        logging.error(f"Changes content: {changes}")