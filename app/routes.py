import subprocess #[cite: 3]
import pyperclip #[cite: 3]
from flask import render_template, url_for, flash, redirect, request #[cite: 3]
from selenium.webdriver.common.by import By #[cite: 3]
from selenium.webdriver.common.keys import Keys #[cite: 3]
from selenium.webdriver.support import expected_conditions as EC #[cite: 3]
from selenium.webdriver.support.ui import Select, WebDriverWait #[cite: 3]

from app import app #[cite: 3]
from app.forms import RegistrationForm, LaunchForm, EpForm #[cite: 3]
from app.automation import (
    get_chrome_driver, 
    create_snow_incident, 
    login_to_servicenow, 
    SNOW_CALL_URL
) #[cite: 3]
from config import Config #[cite: 3]

def run_script(script_path: str) -> None: #[cite: 3]
    """Executes external helper scripts."""
    subprocess.call(['python', script_path]) #[cite: 3]

@app.route("/launch", methods=['GET', 'POST']) #[cite: 3]
def launch(): #[cite: 3]
    form = LaunchForm() #[cite: 3]
    
    first_name = request.form.get("first_name", "") #[cite: 3]
    last_name = request.form.get("last_name", "") #[cite: 3]
    act_dir = request.form.get("act_dir", "") #[cite: 3]
    verify = request.form.get("verify", "") #[cite: 3]
    incident = request.form.get("incident", "") #[cite: 3]
    form_type = form.type.data #[cite: 3]

    if form_type == 'Res': #[cite: 3]
        print('Processing Reset Ticket...')
        desc = f"Customer requests an Active Directory password reset (see ESDKB5809)\nUser ID = \n{act_dir}\nHow was the user verified (2 out of 4 methods per ESDKB6398)? = \n{verify}"
        driver = get_chrome_driver()
        # Changed resolution code to standard PDI value: "Solved (Permanently)"
        create_snow_incident(driver, WebDriverWait(driver, 90), act_dir, "Active Directory Password Reset", desc, "Solved (Permanently)", "Reset password and verified access")

    elif form_type == 'Unl': #[cite: 3]
        print('Processing Unlock Ticket...')
        desc = f"Customer requests an Active Directory password unlock\nUser ID = \n{act_dir}\n{verify}"
        driver = get_chrome_driver()
        # Changed resolution code to standard PDI value: "Solved (Permanently)"
        create_snow_incident(driver, WebDriverWait(driver, 90), act_dir, "Active Directory Password Unlock", desc, "Solved (Permanently)", "Unlocked password and verified access")
        
    elif form_type == 'Gen': #[cite: 3]
        print('Processing General Ticket...') #[cite: 3]
        driver = get_chrome_driver() #[cite: 3]
        create_snow_incident(driver, WebDriverWait(driver, 90), act_dir, None, None, None, None, is_general=True) #[cite: 3]

    elif form_type == 'Bee': #[cite: 3]
        print('Beeping') #[cite: 3]
        driver = get_chrome_driver() #[cite: 3]
        wait = WebDriverWait(driver, 10) #[cite: 3]
        login_to_servicenow(driver, wait) #[cite: 3]
        driver.get(SNOW_CALL_URL) #[cite: 3]
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "gsft_main"))) #[cite: 3]
        
        caller_field = wait.until(EC.element_to_be_clickable((By.ID, "sys_display.new_call.caller"))) #[cite: 3]
        caller_field.send_keys("kenners", Keys.RETURN) #[cite: 3]
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Beeping Call"))).click() #[cite: 3]

    elif form_type == 'Sta': #[cite: 3]
        print('Status') #[cite: 3]
        driver = get_chrome_driver() #[cite: 3]
        wait = WebDriverWait(driver, 10) #[cite: 3]
        login_to_servicenow(driver, wait) #[cite: 3]
        driver.get(SNOW_CALL_URL) #[cite: 3]
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "gsft_main"))) #[cite: 3]
        
        caller_field = wait.until(EC.element_to_be_clickable((By.ID, "sys_display.new_call.caller"))) #[cite: 3]
        caller_field.send_keys(act_dir, Keys.RETURN) #[cite: 3]
        
        Select(wait.until(EC.element_to_be_clickable((By.ID, "new_call.call_type")))).select_by_value("status_call") #[cite: 3]
        Select(wait.until(EC.element_to_be_clickable((By.ID, "new_call.u_task_type")))).select_by_value("Incident") #[cite: 3]
        driver.find_element(By.ID, "sys_display.new_call.u_incident").send_keys(f"INC00{incident}", Keys.RETURN) #[cite: 3]
        driver.find_element(By.ID, "new_call.short_description").send_keys("Status inquiry.") #[cite: 3]

    return render_template('launch.html', title='Launch', form=form) #[cite: 3]

@app.route("/reset", methods=['GET', 'POST']) #[cite: 3]
def reset(): #[cite: 3]
    return render_template('login.html') #[cite: 3]

@app.route('/drop', methods=['GET']) #[cite: 3]
def dropdown(): #[cite: 3]
    types = ['Reset', 'Unlock', 'Beeping', 'Status', 'Ars', 'Gen'] #[cite: 3]
    return render_template('drop.html', types=types) #[cite: 3]