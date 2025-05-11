FROM python:3.12-slim

WORKDIR /app
COPY solax_inverter.py .

RUN pip install --no-cache-dir paho-mqtt aiohttp

CMD ["python", "solax_inverter.py"]
