import os
from dotenv import load_dotenv

load_dotenv()
# >> --- Configuration & Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "bin", "chromedriver.exe")
    SCRIPT_SN_PATH = os.path.join(BASE_DIR, 'scripts', 'cpyxlsclipsn.py')
    SCRIPT_VC_PATH = os.path.join(BASE_DIR, 'scripts', 'cpyxlsclipvc.py')
    ARS_BASE_URL = os.environ.get('ARS_BASE_URL')


