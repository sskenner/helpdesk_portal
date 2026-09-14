import os
import sys

from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

# >> --- Configuration & Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    # --- User generated long, random cryptographic string used by Flask to securely sign session cookies ---
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # --- System Web Addresses ---
    ARS_BASE_URL = os.environ.get('ARS_BASE_URL')
    SNOW_INCIDENT_URL = os.environ.get('SNOW_INCIDENT_URL')
    SNOW_CALL_URL = os.environ.get('SNOW_CALL_URL')
    # --- System Account Info ---
    SNOW_USERNAME = os.environ.get('SNOW_USERNAME')
    SNOW_PASSWORD = os.environ.get('SNOW_PASSWORD')


