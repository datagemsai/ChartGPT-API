FROM python:3.11.4-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY api ./api

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app ./app
COPY chartgpt ./chartgpt
COPY .streamlit ./.streamlit/
COPY media ./media

EXPOSE $PORT
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health

# Multi-page application, after renaming `app/_pages/` to `app/pages/`:
# CMD ["sh", "-c", "python -m streamlit run app/Intro.py --server.port=$PORT --server.address=0.0.0.0"]
# Single-page application:
CMD ["sh", "-c", "python -m streamlit run app/ChartGPT.py --server.port=$PORT --server.address=0.0.0.0"]
