import os
import sys

from flask import Flask

from config import Config


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Anchor to the __init__.py file's folder ('app'), then go up one level to the root
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    return os.path.join(base_path, relative_path)

# 1. Resolve the path to the templates folder
template_dir = get_resource_path('app/templates')

# 2. Initialize Flask with the dynamic template folder
app = Flask(__name__, template_folder=template_dir)

# 3. Load the config from the object
app.config.from_object(Config)

# import routes at the bottom to avoid circular dependencies
from app import routes as routes