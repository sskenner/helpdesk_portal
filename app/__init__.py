from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# import routes at the bottom to avoid circular dependencies
from app import routes