FROM python:3.12-slim

WORKDIR /app

COPY solax_inverter.py .
COPY config.json .

RUN pip install --no-cache-dir requests paho-mqtt

CMD ["python", "solax_inverter.py"]
