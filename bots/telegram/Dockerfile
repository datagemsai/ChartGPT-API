FROM python:3.9.12-slim

WORKDIR /app

COPY api ./api
COPY bots ./bots

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD exec python -m bots.telegram.bot
