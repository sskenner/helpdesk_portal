import time

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config import Config


# --- Helper Functions ---
def get_chrome_driver() -> webdriver.Chrome:
    """Initializes and returns a Chrome WebDriver with performance optimizations."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("detach", True)
    options.page_load_strategy = 'eager'
    options.add_argument("--log-level=3")
    
    return webdriver.Chrome(options=options)

def login_to_servicenow(driver, wait):
    """Logs into the ServiceNow instance using credentials from config."""
    driver.get("https://dev428235.service-now.com/login.do")
    
    username_field = wait.until(EC.element_to_be_clickable((By.ID, "user_name")))
    username_field.send_keys(Config.SNOW_USERNAME)
    
    password_field = driver.find_element(By.ID, "user_password")
    password_field.send_keys(Config.SNOW_PASSWORD)
    
    driver.find_element(By.ID, "sysverb_login").click()
    wait.until(EC.title_contains("ServiceNow"))

def switch_to_snow_iframe(driver, wait):
    """Handles iframe switching for both Classic and Next Experience UI."""
    short_wait = WebDriverWait(driver, 2)

    try:
        # Standard approach: Wait for the iframe directly in the DOM and switch
        short_wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "gsft_main")))
        print("Switched to direct gsft_main iframe.")
    except TimeoutException:
        try:
            # Fallback approach: Pierce the Next Experience Shadow DOM
            shadow_host = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "macroponent-f51912f4c700201072b211d4d8c26010")))
            iframe = shadow_host.shadow_root.find_element(By.CSS_SELECTOR, 'iframe[name="gsft_main"]')
            driver.switch_to.frame(iframe)
            print("Switched to Shadow DOM iframe.")
        except (TimeoutException, NoSuchElementException):
            # No iframe detected (direct URL). Proceed in the main top-level DOM.
            print("No iframe detected. Proceeding in top-level DOM.")

def create_snow_incident(driver, wait, act_dir, service_name, template_text, desc_text, res_code, res_notes, callback_number, is_general=False):    
    login_to_servicenow(driver, wait)
    driver.get(Config.SNOW_INCIDENT_URL)

    # --- Dynamic Wait for Redirects ---
    try:
        wait.until(EC.url_contains("incident.do"))
    except TimeoutException:
        print("Landing page redirect detected. Re-navigating to the incident form...")
        driver.get(Config.SNOW_INCIDENT_URL)
        wait.until(EC.url_contains("incident.do"))

    switch_to_snow_iframe(driver, wait)

    # --- Caller Field AJAX Interaction ---
    caller_field = wait.until(EC.element_to_be_clickable((By.ID, "sys_display.incident.caller_id")))
    caller_field.clear()
    
    # Type the ID one character at a time to force the AJAX listener to trigger
    for char in act_dir:
        caller_field.send_keys(char)
        # time.sleep(0.2) # 500ms pause between each keystroke

    wait.until(lambda d: d.find_element(By.ID, "sys_display.incident.caller_id").get_attribute("aria-expanded") == "true")
    
    # Wait for the database query to complete and the dropdown menu to render
    time.sleep(2) 
    
    # Press DOWN arrow to highlight the first match in the auto-complete dropdown, then ENTER
    caller_field.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.5)
    caller_field.send_keys(Keys.ENTER)
    
    # Allow 1 second for the field to lock in the reference and clear any validation errors
    time.sleep(1)

    # --- Service Field AJAX Interaction ---
    if service_name:
        service_field_id = "sys_display.incident.business_service" 
        
        service_field = wait.until(EC.element_to_be_clickable((By.ID, service_field_id)))
        service_field.clear()
        
        # Type the service name one character at a time to force the AJAX listener to trigger
        for char in service_name:
            service_field.send_keys(char)
            # time.sleep(0.2) 
            
        # Wait for the dropdown menu to render
        wait.until(lambda d: d.find_element(By.ID, service_field_id).get_attribute("aria-expanded") == "true")
        time.sleep(2) 
        
        # Select the top match
        service_field.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.5)
        service_field.send_keys(Keys.ENTER)
        time.sleep(1)

    if not is_general:
        wait.until(EC.presence_of_element_located((By.ID, "incident.short_description")))
        driver.execute_script("g_form.setValue('short_description', arguments[0]);", template_text)
        
        desc = driver.find_element(By.ID, "incident.description")
        desc.clear()
        full_desc = f"{desc_text}\n\nCallback Number: {callback_number}" if callback_number else desc_text
        desc.send_keys(full_desc)
        
        # --- Change State to Resolved to unhide Resolution fields ---
        state_field = wait.until(EC.element_to_be_clickable((By.ID, "incident.state")))
        Select(state_field).select_by_visible_text("Resolved")
        
        # Click the Resolution tab
        res_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Resolution Information')]")))
        driver.execute_script("arguments[0].click();", res_tab)
        
        # Wait for the dropdown options to populate via AJAX
        wait.until(lambda d: len(Select(d.find_element(By.ID, "incident.close_code")).options) > 1)
        
        # --- Select by Index to bypass exact string matching ---
        # Index 0 is "-- None --", Index 1 is the first actual resolution code
        Select(driver.find_element(By.ID, "incident.close_code")).select_by_index(8) 
        
        driver.find_element(By.ID, "incident.close_notes").send_keys(res_notes)

        # --- Prevent form submission pending review ---
        # wait.until(EC.element_to_be_clickable((By.ID, "sysverb_insert"))).click()
        print("Standard form filled successfully. Submission paused.")
        
    else:
        Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.category")))).select_by_value("software") 
        
        wait.until(lambda d: len(Select(d.find_element(By.ID, "incident.subcategory")).options) > 1) 
        Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.subcategory")))).select_by_visible_text("Email") 
        
        desc = driver.find_element(By.ID, "incident.description")
        desc.clear()
        general_desc = f"User ID = \n{act_dir}\nCallback Number: {callback_number}\n" if callback_number else f"User ID = \n{act_dir}\n"

        desc.send_keys(general_desc)
        
        # driver.find_element(By.ID, "sysverb_insert").click()
        print("General form filled successfully. Submission paused.")
