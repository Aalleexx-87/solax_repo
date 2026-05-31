FROM python:3.12-slim

WORKDIR /app

COPY solax_inverter.py /app/solax_inverter.py

RUN pip install --no-cache-dir requests paho-mqtt aiohttp solax==0.3.4

CMD [ "python3", "-u", "/app/solax_inverter.py" ]
