# ChartBot

A Slack bot that uses GPT-3 to generate SQL and Matplotlib charts from free-form analytics texts.

## Overview

The ChartBot app takes in a free-form analytics query via Slack (e.g "How many seed rounds happened in 2022?") and uses GPT-3 to generate SQL and/or charts and return the answer via Slack. The project uses several Python modules and an OpenAI API key, and requires a Slack bot token authenticated against your organization, and an S3 bucket.

## File Structure

The repository contains the following files:
- `base.py`: a Python module that contains helper functions for the ChartBot application.
- `chart.py`: a Python module that handles generating charts from SQL query results.
- `data.py`: a Python module that handles generating SQL queries from data requests.
- `handle_data_request.py`: a Python script that listens to incoming data requests and sends them to the OpenAI API for processing.
- `handle_sql_request.py`: a Python script that listens to incoming SQL requests and sends them to the OpenAI API for processing.
- `make_plot.py`: a Python script that listens to incoming SQL query results, generates matplotlib code to create a chart, and sends the resulting chart to S3.
- `manual_question.py`: a Python script that listens to incoming manually classified questions and adds them to a database for further processing.
- `python.py`: a Python script that connects to a PostgreSQL database and creates a table containing the database schema.
- `readme.md`: a Markdown file containing documentation for the ChartBot application.
- `requirements.txt`: a file containing the Python package dependencies required for running the application.
- `route_question.py`: a Python script that listens to incoming questions and routes them to the appropriate handler based on their classification.
- `scratch.py`: a Python script that contains experimental code for testing and development purposes.

## Dependencies

The following Python packages are required to run the ChartBot application:
- `patterns` (>= 0.12.0)
- `requests` (>= 2.26.0)
- `sqlalchemy` (>= 1.4.22)
- `slack-sdk` (>= 3.11.2)
- `boto3` (>= 1.18.23)
- `matplotlib` (>= 3.4.3)
- `pandas` (>= 1.3.4)

These packages can be installed by running `pip install -r requirements.txt`.

## Usage

To use the ChartBot application, you will need to:
1. Set up an OpenAI API key, a Slack bot token authenticated against your organization, and an S3 bucket.
2. Install the required Python packages listed in `requirements.txt`.
3. Run the `python.py` script to create a table containing the database schema.
4. Start the ChartBot application by running the appropriate Python scripts for handling incoming questions, data requests, SQL requests, and generating charts.
5. Ask questions to the ChartBot via Slack.

## Acknowledgments

This project was created by [Patterns](https://www.patterns.app/) and is licensed under the MIT license.
