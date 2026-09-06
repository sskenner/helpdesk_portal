import pyperclip
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from config import Config

# --- System Web Addresses ---
# SNOW_INCIDENT_URL = "https://nychh.service-now.com/nav_to.do?uri=%2Fincident.do%3Fsys_id%3D-1%26sysparm_query%3Dactive%3Dtrue%26sysparm_stack%3Dincident_list.do%3Fsysparm_query%3Dactive%3Dtrue"
SNOW_INCIDENT_URL = "https://dev428235.service-now.com/nav_to.do?uri=%2Fincident.do%3Fsys_id%3D-1%26sysparm_query%3Dactive%3Dtrue%26sysparm_stack%3Dincident_list.do%3Fsysparm_query%3Dactive%3Dtrue"
SNOW_CALL_URL = "https://dev428235.service-now.com/new_call.do?sys_id=-1&sysparm_stack=new_call_list.do"

# --- Helper Functions ---
def get_chrome_driver() -> webdriver.Chrome:
    """Initializes and returns a Chrome WebDriver with performance optimizations."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("detach", True)
    
    # Eager strategy stops waiting for full stylesheets/images, drastically improving execution speed.
    options.page_load_strategy = 'eager'

    # suppress Chrome background terminal warning if on corp
    options.add_argument("--log-level=3")
    
    try:
        return webdriver.Chrome(executable_path=Config.CHROMEDRIVER_PATH, options=options)
    #TODO ?? what does it fallback too?
    except Exception:
        # Fallback if the path is not found or config fails
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

def switch_to_snow_iframe(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """Handles Shadow DOM and iframe switching for ServiceNow (Selenium 4+ compatible)."""
    shadow_host = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'macroponent-f51912f4c700201072b211d4d8c26010')))
    
    # Modern Selenium 4 native Shadow DOM handling (no dictionary parsing needed)
    shadow_root = shadow_host.shadow_root
    
    # Wait for the iframe to appear inside the shadow root and switch to it
    iframe = WebDriverWait(shadow_root, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[name="gsft_main"]')))
    driver.switch_to.frame(iframe)

def create_snow_incident(driver, wait, act_dir, callback, template_text, desc_text, res_code, res_notes, is_general=False):
    """Handles the robust form filling for Res, Unl, and Gen tickets with explicit waits."""
    login_to_servicenow(driver, wait)

    driver.get(SNOW_INCIDENT_URL)
    switch_to_snow_iframe(driver, wait)
    
    # Init Caller
    shadow_content_iframe = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#sys_display\\.incident\\.caller_id')))
    shadow_content_iframe.click()
    
    caller_field = wait.until(EC.element_to_be_clickable((By.ID, "sys_display.incident.caller_id")))
    caller_field.send_keys(act_dir, Keys.RETURN)
    
    wait.until(EC.visibility_of_element_located((By.ID, "templates-list-container")))

    # TODO verify distiguishes btw reset & unlock agent selections/choices
    if not is_general:
        # Standard workflow for Reset and Unlock
        template_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, template_text)))
        template_btn.click()
        
        # Wait for the template to populate the description field via AJAX
        wait.until(lambda d: d.find_element(By.ID, "incident.description").get_attribute("value") != "")
        
        caller_phone = wait.until(EC.element_to_be_clickable((By.ID, "incident.u_caller_business_phone")))
        caller_phone.clear()
        caller_phone.send_keys(callback)
        
        on_behalf = driver.find_element(By.ID, "sys_display.incident.u_on_behalf_of")
        on_behalf.clear()
        on_behalf.send_keys(act_dir, Keys.RETURN)
        
        behalf_phone = wait.until(EC.element_to_be_clickable((By.ID, "incident.u_onbehalfof_business_phone")))
        behalf_phone.clear()
        behalf_phone.send_keys(callback)
        
        desc = driver.find_element(By.ID, "incident.description")
        desc.clear()
        desc.send_keys(desc_text)
        
        res_field = driver.find_element(By.ID, "incident.close_code")
        driver.execute_script("arguments[0].scrollIntoView();", res_field)
        Select(res_field).select_by_value(res_code)
        
        driver.find_element(By.ID, "incident.close_notes").send_keys(res_notes)
        
        # Invalid reference magnifier fallback
        try:
            if driver.find_elements(By.XPATH, "//*[contains(text(), 'Invalid reference')]"):
                driver.find_element(By.ID, "lookup.incident.u_on_behalf_of").click()
                main_win = driver.window_handles[0]
                wait.until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[1])
                
                search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
                search_box.send_keys(act_dir, Keys.RETURN)
                
                ref_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "glide_ref_item_link")))
                ref_link.click()
                
                driver.switch_to.window(main_win)
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "gsft_main")))
        except Exception:
            pass
            
        wait.until(EC.element_to_be_clickable((By.ID, "sysverb_update_save_stay_bottom"))).send_keys(Keys.NULL)
        
    else:
        # General workflow
        caller_phone = wait.until(EC.element_to_be_clickable((By.ID, "incident.u_caller_business_phone")))
        caller_phone.clear()
        caller_phone.send_keys(callback)
        
        on_behalf = driver.find_element(By.ID, "sys_display.incident.u_on_behalf_of")
        on_behalf.clear()
        on_behalf.send_keys(act_dir, Keys.RETURN)
        
        behalf_phone = wait.until(EC.element_to_be_clickable((By.ID, "incident.u_onbehalfof_business_phone")))
        behalf_phone.clear()
        behalf_phone.send_keys(callback)
        
        Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.u_request_type")))).select_by_value("Incident")
        Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.category")))).select_by_value("Software Application")
        Select(wait.until(EC.element_to_be_clickable((By.ID, "incident.subcategory")))).select_by_value("Error / Malfunction")
        
        desc = driver.find_element(By.ID, "incident.description")
        desc.clear()
        desc.send_keys(f"User ID = \n{act_dir}\n")
        
        driver.find_element(By.ID, "4c1cfa36c611227501e6728036d9723b").click()
        
        res_field = wait.until(EC.element_to_be_clickable((By.ID, "incident.close_code")))
        driver.execute_script("arguments[0].scrollIntoView();", res_field)
        Select(res_field).select_by_value("Updated")
        
        try:
            if driver.find_elements(By.XPATH, "//*[contains(text(), 'Invalid reference')]"):
                driver.find_element(By.ID, "lookup.incident.u_on_behalf_of").click()
                main_win = driver.window_handles[0]
                wait.until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[1])
                
                search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
                search_box.send_keys(act_dir, Keys.RETURN)
                
                ref_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "glide_ref_item_link")))
                ref_link.click()
                
                driver.switch_to.window(main_win)
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "gsft_main")))
                driver.find_element(By.ID, "resolve_incident").send_keys(Keys.NULL)
        except Exception:
            driver.find_element(By.ID, "incident.description").send_keys(Keys.NULL)

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
