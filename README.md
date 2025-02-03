# ChartGPT API

- An AI agent capable of performing complex data analytics queries to answer natural language questions.
- Streamed chatbot-style responses and Plotly visualisations.
- Robust error handling and correction.
- Developed using OpenAI's API.
- Accepts Google BigQuery as a data source and capable of multi-table queries.

## Development

### Python Environment

Python 3.11 environment using dependencies from [requirements.txt](requirements.txt).

### MongoDB

For local development, start a MongoDB Docker container.

```bash
docker run -p 27017:27017 --name mongo -d mongodb/mongodb-community-server:latest
```

### Secrets and Environment Variables

For production, secrets and environment variables are set in a `app_secrets_{environment}.yaml` file during deployment.

For local development, secrets and environment variables are loaded using the Python `python-dotenv` package from a `.env` file.

Make a copy of [.env.example](.env.example) to [.env](.env) and fill in the relevant variables from Keeper.

[.env](.env) should not be committed to git and is included in the [.gitignore](.gitignore) file.

#### Google Auth

For production, Google Cloud Platform will authenticate using the application's default service account.

For local development:
1. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install): e.g. `sudo snap install google-cloud-cli`
2. Set up Google [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc): `gcloud auth application-default login`
3. Set default GCP project (for now we'll cautiously use the production project until we have a staging environment with datasets): `gcloud config set project psychic-medley-383515`

## Google IAM

The Google Service Account used for the production app should be given the following roles:
* BigQuery Data Viewer
* BigQuery Job User
* BigQuery Read Session User
* Cloud Datastore User
* Firebase Admin SDK Administrator Service Agent

For developer access to BigQuery, where they are required to create and delete datasets, the Service Account should additionally have the following permissions:
* BigQuery User
* BigQuery Data Editor

## Google Cloud Firestore

Cloud Firestore is used for storing analytics about queries and responses.

In a new GCP projects, you'll need to enable the Cloud Firestore API and create a new database using "Native Mode".

## App Engine Deployment

### Production

Default region: Frankfurt `europe-west3`

```bash
gcloud config set project chartgpt-production
gcloud config set app/cloud_build_timeout 1600
gcloud app deploy --project=chartgpt-production app_production.yaml
```

## Cloud SQL

```bash
gcloud auth login
gcloud auth application-default login
gcloud services enable sqladmin.googleapis.com
# Get cloud-sql-proxy from source for relevant operating system
chmod +x cloud-sql-proxy
./cloud-sql-proxy $CONNECTION_NAME
```
