# Azure Serverless Sensor Data Pipeline

This repository contains a serverless data processing project built using **Azure Functions, Python and Azure SQL**.

The project simulates sensor data, stores it in an Azure SQL database and uses serverless functions to process the data and calculate sensor statistics.

## Project Overview

Each sensor reading contains:

- Temperature
- Wind speed
- Relative humidity
- CO₂ level

Two implementations are included:

- HTTP-triggered implementation
- Timer-triggered implementation

## Demo

A short demonstration of the serverless sensor data pipeline:

[Watch the project demo](demo/Azure%20demo%20video.mp4)

## HTTP-Triggered Implementation

The HTTP-triggered version is located in:

```text
http-triggered/function_app.py
```

It provides an HTTP POST endpoint that generates simulated sensor readings and inserts them into the Azure SQL `SensorData` table.

The number of readings can be supplied in the request, with a default of 20 and a maximum of 1000.

An SQL trigger runs when the database changes and calculates minimum, maximum and average values for each sensor.

This implementation was also used for scalability testing.

## Timer-Triggered Implementation

The timer-triggered version is located in:

```text
timer-triggered/function_app.py
```

It automatically generates and inserts **20 sensor readings every 10 seconds**.

When new data is inserted, an SQL trigger calculates statistics for each sensor.

## Scalability Testing

The HTTP-triggered implementation was tested under different request loads.

The resulting performance graphs are included in the `scalability-results` folder.

## Technologies

- Python
- Microsoft Azure Functions
- Azure SQL Database
- SQL
- PyODBC

## Database

The project uses an Azure SQL `SensorData` table containing:

- `sensor_id`
- `temperature`
- `wind`
- `relative_humidity`
- `co2`

The functions calculate minimum, maximum and average values for temperature, wind, humidity and CO₂.

## Installation

It is recommended to use a virtual environment.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Azure Functions Core Tools is required to run the project locally.

## Configuration

Open:

```text
local.settings.json
```

and replace the existing `SqlConnectionString` value with the connection string for your own Azure SQL database.

The connection string should point to a database containing the `SensorData` table.

## Running the Project

Both implementations use the Azure Functions entry-point filename:

```text
function_app.py
```

To run either version, place the relevant `function_app.py` in the Azure Functions project directory alongside:

```text
host.json
local.settings.json
requirements.txt
```

Then run:

```bash
func start
```

Use the HTTP-triggered version for manual requests and scalability testing.

Use the timer-triggered version to automatically generate sensor data every 10 seconds.

## Author

Joseph Abraham Thekkedam
