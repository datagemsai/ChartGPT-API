# ChartGPT
[![Build Status](https://github.com/***REMOVED***/ChartGPT/actions/workflows/python.yml/badge.svg)](https://github.com/***REMOVED***/ChartGPT/actions/workflows/python.yml)

- [(Deprecated) analytics_bot/](analytics_bot/): Code based on https://www.patterns.app/blog/2023/02/07/chartbot-sql-analyst-gpt using OpenAI's davinci LLM directly via the API.
- [analytics_bot_langchain/](analytics_bot_langchain/): LangChain-based BigQuery analytics agent "toolkit" using OpenAI's GPT-3.5-turbo LLM, see [notebooks/bigquery_agent_toolkit.ipynb](notebooks/bigquery_agent_toolkit.ipynb) for a demo. This code has been structured to match the software architecture of LangChain as much as possible, to remain compatible and be able to make PRs back to public repo.

## Development

### Python Environment

Standard ***REMOVED*** Python environment using dependencies from [requirements.txt](requirements.txt).

### Secrets and Environment Variables

For production, secrets and environment variables are set in a `secrets.yaml` file during deployment.

For local development, secrets and environment variables are loaded using the Python `python-dotenv` package from a `.env` file.

Make a copy of [.env.example](.env.example) to [.env](.env) and fill in the relevant variables from Keeper.

[.env](.env) should not be committed to git and is included in the [.gitignore](.gitignore) file.

#### Google Auth

##### Google Cloud Platform Deployment

For production, Google Cloud Platform will authenticate using the application's default service account.

For local development:
1. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install): e.g. `sudo snap install google-cloud-cli`
2. Set up Google [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc): `gcloud auth application-default login`

### Streamlit

Edit `app/ChartGPT.py` to customize this app to your heart's desire. :heart:

Run Streamlit app locally using `make run` - open in a browser and edit the code live.

If you have any questions, check out the Streamlit [documentation](https://docs.streamlit.io) and [community
forum](https://discuss.streamlit.io).

## Google BigQuery

The Google Service Account used for the production app should be given the following roles:
* BigQuery Data Viewer
* BigQuery Job User
* BigQuery Read Session User

For developer access to BigQuery, where they are required to create and delete datasets, the Service Account should additionally have the following permissions:
* BigQuery User
* BigQuery Data Editor
