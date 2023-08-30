FROM python:3.11.4-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY api ./api
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

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
# CMD ["sh", "-c", "python -m streamlit run app/Home.py --server.port=$PORT --server.address=0.0.0.0"]
CMD ["/usr/bin/supervisord"]
