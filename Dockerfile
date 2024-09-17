FROM python:3.12-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_RUN_PORT=8080
EXPOSE 8080

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]