FROM python:3.11-slim
LABEL authors="safronCode"
WORKDIR /tgbot
COPY . tgbot-voicerelay/
WORKDIR /tgbot/tgbot-voicerelay



COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED 1

COPY . .
CMD ["python", "start_project.py"]
