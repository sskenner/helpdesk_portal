import subprocess
import pyperclip
from flask import render_template, url_for, flash, redirect, request
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from app import app
from app.forms import RegistrationForm, LaunchForm, EpForm
from app.automation import (
    get_chrome_driver, 
    create_snow_incident, 
    login_to_servicenow, 
    SNOW_CALL_URL
)
from config import Config

def run_script(script_path: str) -> None:
    """Executes external helper scripts[cite: 1]."""
    subprocess.call(['python', script_path])

@app.route("/launch", methods=['GET', 'POST'])
def launch():
    form = LaunchForm()
    
    first_name = request.form.get("first_name", "")
    last_name = request.form.get("last_name", "")
    callback = request.form.get("callback", "")
    act_dir = request.form.get("act_dir", "")
    verify = request.form.get("verify", "")
    incident = request.form.get("incident", "")
    form_type = form.type.data

    if form_type == 'Res':
        print('Processing Reset Ticket...')
        desc = f"Customer requests an Active Directory password reset (see ESDKB5809)\nUser ID = \n{act_dir}\nHow was the user verified (2 out of 4 methods per ESDKB6398)? = \n{verify}"
        driver = get_chrome_driver()
        create_snow_incident(driver, WebDriverWait(driver, 15), act_dir, callback, "Active Directory Password Reset", desc, "Reset/Unlock Password", "Reset password and verified access")

    elif form_type == 'Unl':
        print('Processing Unlock Ticket...')
        desc = f"Customer requests an Active Directory password unlock\nUser ID = \n{act_dir}\n{verify}"
        driver = get_chrome_driver()
        create_snow_incident(driver, WebDriverWait(driver, 15), act_dir, callback, "Active Directory Password Unlock", desc, "Reset/Unlock Password", "Unlocked password and verified access")
        
    elif form_type == 'Gen':
        print('Processing General Ticket...')
        driver = get_chrome_driver()
        create_snow_incident(driver, WebDriverWait(driver, 15), act_dir, callback, None, None, None, None, is_general=True)

    elif form_type == 'Bee':
        print('Beeping')
        driver = get_chrome_driver()
        wait = WebDriverWait(driver, 10)
        login_to_servicenow(driver, wait)
        driver.get(SNOW_CALL_URL)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "gsft_main")))
        
        caller_field = wait.until(EC.element_to_be_clickable((By.ID, "sys_display.new_call.caller")))
        caller_field.send_keys("kenners", Keys.RETURN)
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Beeping Call"))).click()

    elif form_type == 'Sta':
        print('Status')
        driver = get_chrome_driver()
        wait = WebDriverWait(driver, 10)
        login_to_servicenow(driver, wait)
        driver.get(SNOW_CALL_URL)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "gsft_main")))
        
        caller_field = wait.until(EC.element_to_be_clickable((By.ID, "sys_display.new_call.caller")))
        caller_field.send_keys(act_dir, Keys.RETURN)
        
        Select(wait.until(EC.element_to_be_clickable((By.ID, "new_call.call_type")))).select_by_value("status_call")
        Select(wait.until(EC.element_to_be_clickable((By.ID, "new_call.u_task_type")))).select_by_value("Incident")
        driver.find_element(By.ID, "sys_display.new_call.u_incident").send_keys(f"INC00{incident}", Keys.RETURN)
        driver.find_element(By.ID, "new_call.short_description").send_keys("Status inquiry.")

    return render_template('launch.html', title='Launch', form=form)

@app.route("/reset", methods=['GET', 'POST'])
def reset():
    # Placeholder for LoginForm validation[cite: 1]
    return render_template('login.html')

@app.route('/drop', methods=['GET'])
def dropdown():
    types = ['Reset', 'Unlock', 'Beeping', 'Status', 'Ars', 'Gen']
    return render_template('drop.html', types=types)