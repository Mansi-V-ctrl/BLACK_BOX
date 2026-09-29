# BLACK BOX

## Application Event Monitoring & Incident Reconstruction Platform

BLACK BOX is a Flask and MySQL based application event monitoring and incident reconstruction platform.

## Technology

- HTML
- CSS
- JavaScript
- Python Flask
- MySQL
- mysql-connector-python
- Chart.js

## Features

- User registration and login
- Public landing page
- Logged-in workspace
- Automatic application event generation
- Event monitoring
- Rule-based abnormal pattern detection
- Possible incident detection
- Incident creation
- Incident timeline reconstruction
- Root cause recording
- Resolution tracking
- Dashboard statistics
- Charts

## Database

The project uses six main tables:

1. users
2. applications
3. events
4. incidents
5. incident_events
6. resolutions

## Installation

Create a virtual environment:

python -m venv venv

Activate it:

.\venv\Scripts\Activate.ps1

Install requirements:

pip install -r requirements.txt

## Database Setup

Run schema.sql using MySQL Command Line Client.

## Configuration

Update MySQL credentials in config.py.

## Run

python app.py

Open:

http://127.0.0.1:5000/

## Demo Flow

Register a user.

Login.

Open Demo App.

Generate normal events.

Generate timeout, retry and payment failed events.

After multiple failed events, BLACK BOX detects a possible incident.

Create the incident.

Start investigation.

Review the timeline.

Add root cause and resolution.

Mark the incident as resolved.