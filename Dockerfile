FROM python:3.9-slim
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./f1_telemetry ./f1_telemetry
CMD ["python3", "-m", "f1_telemetry.dashboard.app"]
