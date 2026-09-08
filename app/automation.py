import pyperclip
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import Config

# --- System Web Addresses ---
# SNOW_INCIDENT_URL = "https://dev428235.service-now.com/nav_to.do?uri=%2Fincident.do%3Fsys_id%3D-1%26sysparm_query%3Dactive%3Dtrue%26sysparm_stack%3Dincident_list.do%3Fsysparm_query%3Dactive%3Dtrue" #[cite: 1]
SNOW_INCIDENT_URL = "https://dev428235.service-now.com/incident.do?sys_id=-1"
SNOW_CALL_URL = "https://dev428235.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do" #[cite: 1]

# --- Helper Functions ---
def get_chrome_driver() -> webdriver.Chrome:
    """Initializes and returns a Chrome WebDriver with performance optimizations."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("detach", True)
    options.page_load_strategy = 'eager' #[cite: 1]
    options.add_argument("--log-level=3") #[cite: 1]
    
    try:
        return webdriver.Chrome(executable_path=Config.CHROMEDRIVER_PATH, options=options) #[cite: 1]
    except Exception:
        return webdriver.Chrome(options=options) #[cite: 1]

def login_to_servicenow(driver, wait):
    """Logs into the ServiceNow instance using credentials from config."""
    driver.get("https://dev428235.service-now.com/login.do") #[cite: 1]
    
    username_field = wait.until(EC.element_to_be_clickable((By.ID, "user_name"))) #[cite: 1]
    username_field.send_keys(Config.SNOW_USERNAME) #[cite: 1]
    
    password_field = driver.find_element(By.ID, "user_password") #[cite: 1]
    password_field.send_keys(Config.SNOW_PASSWORD) #[cite: 1]
    
    driver.find_element(By.ID, "sysverb_login").click() #[cite: 1]
    wait.until(EC.title_contains("ServiceNow")) #[cite: 1]

def switch_to_snow_iframe(driver, wait):
    """Handles iframe switching for both Classic and Next Experience UI."""
    short_wait = WebDriverWait(driver, 3)

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
            pass

def create_snow_incident(driver, wait, act_dir, template_text, desc_text, res_code, res_notes, is_general=False):
    login_to_servicenow(driver, wait)
    driver.get(SNOW_INCIDENT_URL)

    # --- FIX: Handle Post-Login Redirects ---
    # Allow the PDI's background login scripts 3 seconds to execute any forced redirects
    time.sleep(3)

    # Check if the platform hijacked the URL away from the incident form
    if "incident.do" not in driver.current_url:
        print("Landing page redirect detected. Re-navigating to the incident form...")
        driver.get(SNOW_INCIDENT_URL)

    switch_to_snow_iframe(driver, wait)

    # --- Caller Field AJAX Interaction ---
    caller_field = wait.until(EC.element_to_be_clickable((By.ID, "sys_display.incident.caller_id")))
    caller_field.clear()
    
    # Type the ID one character at a time to force the AJAX listener to trigger
    for char in act_dir:
        caller_field.send_keys(char)
        time.sleep(0.5) # 500ms pause between each keystroke

    wait.until(lambda d: d.find_element(By.ID, "sys_display.incident.caller_id").get_attribute("aria-expanded") == "true")
    
    # Wait for the database query to complete and the dropdown menu to render
    time.sleep(2) 
    
    # Press DOWN arrow to highlight the first match in the auto-complete dropdown, then ENTER
    caller_field.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.5)
    caller_field.send_keys(Keys.ENTER)
    
    # Allow 1 second for the field to lock in the reference and clear any validation errors
    time.sleep(1)

    # 1. Execute the iframe switch
    # switch_to_snow_iframe(driver, wait)
    
    # 2. Proceed with field interaction using g_form
    # wait.until(EC.presence_of_element_located((By.ID, "sys_display.incident.caller_id")))
    # driver.execute_script("g_form.setValue('caller_id', arguments[0]);", act_dir)

    if not is_general:
        wait.until(EC.presence_of_element_located((By.ID, "incident.short_description")))
        driver.execute_script("g_form.setValue('short_description', arguments[0]);", template_text)
        
        desc = driver.find_element(By.ID, "incident.description")
        desc.clear()
        desc.send_keys(desc_text)
        
        # --- FIX: Change State to Resolved to unhide Resolution fields ---
        state_field = wait.until(EC.element_to_be_clickable((By.ID, "incident.state")))
        Select(state_field).select_by_visible_text("Resolved")
        
        # Click the Resolution tab
        res_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Resolution Information')]")))
        driver.execute_script("arguments[0].click();", res_tab)
        
        # Locate the Resolution Code dropdown
        res_field = wait.until(EC.presence_of_element_located((By.ID, "incident.close_code")))
        
        # Wait for the dropdown options to populate via AJAX
        wait.until(lambda d: len(Select(d.find_element(By.ID, "incident.close_code")).options) > 1)
        
        # --- FIX: Select by Index to bypass exact string matching ---
        # Index 0 is "-- None --", Index 1 is the first actual resolution code
        Select(driver.find_element(By.ID, "incident.close_code")).select_by_index(1) 
        
        driver.find_element(By.ID, "incident.close_notes").send_keys(res_notes)

        # --- FIX: Prevent form submission ---
        # wait.until(EC.element_to_be_clickable((By.ID, "sysverb_insert"))).click()
        print("Standard form filled successfully. Submission paused.")
        
    else:
        Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.category")))).select_by_value("software") 
        
        wait.until(lambda d: len(Select(d.find_element(By.ID, "incident.subcategory")).options) > 1) 
        Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.subcategory")))).select_by_visible_text("Email") 
        
        desc = driver.find_element(By.ID, "incident.description")
        desc.clear()
        desc.send_keys(f"User ID = \n{act_dir}\n")
        
        # driver.find_element(By.ID, "sysverb_insert").click()
        print("General form filled successfully. Submission paused.")

    # if not is_general:
    #     # Standard workflow for Reset and Unlock - inject directly instead of using templates
    #     wait.until(EC.presence_of_element_located((By.ID, "incident.short_description")))
    #     driver.execute_script("g_form.setValue('short_description', arguments[0]);", template_text)
    # # wait.until(EC.visibility_of_element_located((By.ID, "templates-list-container"))) #[cite: 1]

    # # if not is_general: #[cite: 1]
    # #     # Standard workflow for Reset and Unlock
    # #     template_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, template_text))) #[cite: 1]
    # #     template_btn.click() #[cite: 1]
        
    # #     wait.until(lambda d: d.find_element(By.ID, "incident.description").get_attribute("value") != "") #[cite: 1]
        
    #     desc = driver.find_element(By.ID, "incident.description") #[cite: 1]
    #     desc.clear() #[cite: 1]
    #     desc.send_keys(desc_text) #[cite: 1]
        
    #     # PDI standard closure fields
    #     res_field = driver.find_element(By.ID, "incident.close_code") #[cite: 1]
    #     driver.execute_script("arguments[0].scrollIntoView();", res_field) #[cite: 1]
    #     Select(res_field).select_by_value(res_code) #[cite: 1]
        
    #     driver.find_element(By.ID, "incident.close_notes").send_keys(res_notes) #[cite: 1]
        
    #     wait.until(EC.element_to_be_clickable((By.ID, "sysverb_insert"))).click() # PDI submit button, replaces enterprise sys_id[cite: 1]
        
    # else: #[cite: 1]
    #     # General workflow with dependent dropdown waits
    #     Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.category")))).select_by_value("software") # Standard PDI category value[cite: 1]
        
    #     # Wait for the subcategory DOM to dynamically repopulate based on category selection
    #     wait.until(lambda d: len(Select(d.find_element(By.ID, "incident.subcategory")).options) > 1) 
    #     Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.subcategory")))).select_by_visible_text("Email") # Standard PDI subcategory value[cite: 1]
        
    #     desc = driver.find_element(By.ID, "incident.description") #[cite: 1]
    #     desc.clear() #[cite: 1]
    #     desc.send_keys(f"User ID = \n{act_dir}\n") #[cite: 1]
        
    #     # Standard PDI submit action
    #     driver.find_element(By.ID, "sysverb_insert").click() 

# (process_servicenow_report and process_vcc_report remain unchanged as they target different modules/dashboards)
def process_servicenow_report() -> None:
    """Logs into the ticketing dashboard and downloads current daily performance data."""
    print('FTRsn: Opening YK report...')
    driver = get_chrome_driver()
    driver.maximize_window()

    login_to_servicenow(driver, wait)
    
    driver.get(SNOW_REPORT_URL)
    wait = WebDriverWait(driver, 10)
    
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "gsft_main")))
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[starts-with(@id, 'cal_GwtGFD_')]"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/table/tbody/tr/td/table/tbody/tr/td[2]/h1/div/table/tbody/tr/td/table/tbody/tr[9]/td"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/table/tbody/tr/td/table/tbody/tr/td[4]/button[1]"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/form/div/div[1]/div[2]/div/div[1]/div/div/table[1]/tbody/tr/td/table/tbody/tr[6]/td/table/tbody/tr/td[4]/button[1]"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/table/tbody/tr/td/table/tbody/tr/td[2]/h1/div/table/tbody/tr/td/table/tbody/tr[9]/td"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/table/tbody/tr/td/table/tbody/tr/td[4]/button[1]"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/form/nav/div/div/div[2]/div/div/a[1]"))).click()
    
    click_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/table/tbody/tr/td/div[1]/div/span/div/div[2]/table/tbody/tr/td/div/table/thead/tr/th[5]")))
    ActionChains(driver).move_to_element(click_menu).context_click(click_menu).perform()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div[15]"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[2]"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/table/tbody/tr[2]/td/span/rendered_body/table/tbody/tr[6]/td/button[2]"))).click()

def process_vcc_report() -> None:
    """Logs into the call center dashboard to export the latest call volume statistics."""
    print('FTRvc: Opening VCC data downloads...')
    driver = get_chrome_driver()
    driver.maximize_window()
    driver.get(VCC_BASE_URL)
    wait = WebDriverWait(driver, 10)
    
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/form/app-root/app-home/div/cxone-header/header/div[3]")))
    driver.get(VCC_DATA_URL)
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/form/app-root/app-home/div/cxone-header/header/div[3]")))
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/form/div[4]/div/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[3]/div[2]/div[1]/table/tbody/tr/td[9]/table/tbody/tr/td"))).click()
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/form/div[4]/div/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/table/tbody/tr[6]/td[2]"))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/form/div[4]/div/div/div/div/div[2]/div[1]/div/div[2]/div[1]/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/div/input")))
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/form/div[4]/div/div/div/div/div[2]/div[1]/div/div[2]/div[1]/table/tbody/tr[1]/td/table/tbody/tr[4]/td[2]/table/tbody/tr/td[1]/input"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/form/div[4]/div/div/div/div/div[2]/div[1]/div/div[2]/div[1]/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/div/div/input"))).click()