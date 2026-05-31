FROM python:3.12-slim

WORKDIR /app

COPY solax_inverter.py /app/solax_inverter.py

RUN echo ">>> BUILD OK <<<"

CMD ["sh", "-c", "echo '>>> CONTAINER STARTED <<<'; python3 -u /app/solax_inverter.py"]
