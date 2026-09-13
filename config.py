import os

from dotenv import load_dotenv

load_dotenv()
# >> --- Configuration & Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "bin", "chromedriver.exe")
    # --- System Web Addresses ---
    ARS_BASE_URL = os.environ.get('ARS_BASE_URL')
    SNOW_INCIDENT_URL = os.environ.get('SNOW_INCIDENT_URL')
    SNOW_CALL_URL = os.environ.get('SNOW_CALL_URL')
    # --- System Account Info ---
    SNOW_USERNAME = os.environ.get('SNOW_USERNAME')
    SNOW_PASSWORD = os.environ.get('SNOW_PASSWORD')


