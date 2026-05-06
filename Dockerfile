FROM python:3.12-slim

WORKDIR /app
COPY solax_inverter.py .

RUN pip install --no-cache-dir paho-mqtt aiohttp solax==0.3.2

CMD ["python", "solax_inverter.py"]
