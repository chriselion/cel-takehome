from flask import Flask
from src.types import Location  # noqa

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"