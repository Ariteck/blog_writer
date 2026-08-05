FROM python:3.14.6

WORKDIR /app
ENV PYTHONPATH=/app
COPY requirements.txt .
COPY src ./src
COPY run.py .
COPY .env .
RUN pip install --no-cache-dir -r requirements.txt

RUN 

EXPOSE 8080



CMD ["python", "run.py"]
