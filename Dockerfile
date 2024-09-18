FROM python:3.12-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# TODO add users so that the web server isn't running as root

ENV FLASK_RUN_PORT=8080
EXPOSE 8080

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
