
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# ========= Please enter the following configuration=========
EMAIL = "your_email@example.com"
PASSWORD = "your_password_here"
ACCOUNT_ENTERING_TIME = 20
PAGE_CHANGE_TIME = 1
# ===========================================================

# CSS selectors
ITEM_SELECTOR = "div.gX_vOH"
NAME_SELECTOR = "div.NgcapS"
POOL_SELECTOR = "div.xWZ6Cb"
NEW_SELECTOR = "div.QnXVrG"
TIME_SELECTOR = "div.r9iEWS"
NEXT_BUTTON_SELECTOR = "div.v8UsPN"
EMAIL_INPUT = "input[name='email']"
PASSWORD_INPUT = "input[type='password']"
LOGIN_BUTTON = "button[type='submit']"

STAR_SELECTOR_6 = ".rT1IyY.UN5Fou"
STAR_SELECTOR_5 = ".rT1IyY.A0qObD"
STAR_SELECTOR_4 = ".rT1IyY.spIT3K"
STAR_SELECTOR_3 = ".rT1IyY.Ff2rvO"


# Chrome options
options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    # initialize
    driver.get("https://ak.gryphline.com/user/visit")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, EMAIL_INPUT)))
    
    
    if EMAIL == "your_email@example.com":
        time.sleep(ACCOUNT_ENTERING_TIME)
    else:
        time.sleep(2*PAGE_CHANGE_TIME)
        try:
            driver.find_element(By.CSS_SELECTOR, EMAIL_INPUT).send_keys(EMAIL)
            driver.find_element(By.CSS_SELECTOR, PASSWORD_INPUT).send_keys(PASSWORD)
        except NoSuchElementException:
            print("login elements not found.")
            driver.quit()
            exit()
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, LOGIN_BUTTON)))
        login_button.click()
        time.sleep(5*PAGE_CHANGE_TIME)

    # page collection
    records = []
    last_page = []
    current_page = []
    while True:
        items = driver.find_elements(By.CSS_SELECTOR, ITEM_SELECTOR)
        if not items:
            print("no items found.")
            break
        
        for item in items:
            try:
                # get operator name and time
                name = item.find_element(By.CSS_SELECTOR, NAME_SELECTOR).text
                t = item.find_element(By.CSS_SELECTOR, TIME_SELECTOR).text
                # get pool name
                pool = "Unknown"
                try:
                    temp = item.find_element(By.CSS_SELECTOR, POOL_SELECTOR).text
                    if len(temp) > 0:
                        pool = temp
                except NoSuchElementException:
                    pass
                # star check
                star = "0"
                for cls, val in [(STAR_SELECTOR_3, "3"), 
                                 (STAR_SELECTOR_4, "4"),
                                 (STAR_SELECTOR_5, "5"),
                                 (STAR_SELECTOR_6, "6")]:
                    try:
                        item.find_element(By.CSS_SELECTOR, cls)
                        star = val
                        break
                    except NoSuchElementException:
                        continue

                # new check
                try:
                    item.find_element(By.CSS_SELECTOR, NEW_SELECTOR)
                    new = "True"
                except NoSuchElementException:
                    new = "False"
                records.append({"operator": name,"star": star,"pool": pool,"time": t,"new": new})
                current_page.append(t)
            except NoSuchElementException:
                print("Operator name or time not found.")
                continue

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, NEXT_BUTTON_SELECTOR)
            if 'disabled' in next_btn.get_attribute('class'):
                break
            next_btn.click()
            time.sleep(PAGE_CHANGE_TIME)
        except NoSuchElementException:
            break
        if current_page == last_page:
            print("Scraping completed, no new items found.")
            break
        last_page = current_page.copy()
        current_page.clear()

finally:
    driver.quit()


# check previous json
import json
previous_records = []
try:
    with open("visit_records.json", "r", encoding="utf-8") as f:
        previous_records = json.load(f)
except FileNotFoundError:
    print("visit_records.json not found, creating a new one.")

if len(previous_records) > 0 and len(records) > 0:
    # Compare records cluster by cluster (records with the same "time")
    cursor_now = 0
    cursor_prev = 0
    while cursor_now < len(records) and cursor_prev < len(previous_records):
        cursor_now_bak = cursor_now
        cursor_prev_bak = cursor_prev
        # Find the next cluster (records with the same "time")
        cluster_now = [records[cursor_now]]
        cluster_prev = [previous_records[cursor_prev]]
        # If the time is the same, put into the same cluster
        cursor_now += 1
        cursor_prev += 1
        while cursor_now < len(records) and records[cursor_now]["time"] == cluster_now[0]["time"]:
            cluster_now.append(records[cursor_now])
            cursor_now += 1
        while cursor_prev < len(previous_records) and previous_records[cursor_prev]["time"] == cluster_prev[0]["time"]:
            cluster_prev.append(previous_records[cursor_prev])
            cursor_prev += 1
        # Compare the two clusters
        if len(cluster_now) == 0 or len(cluster_prev) == 0:
            break
        elif cluster_now[0]["time"] == cluster_prev[0]["time"]:
            # If the time is the same, compare the records
            if len(cluster_now) == len(cluster_prev):
                # keep the new records
                for i in range(len(cluster_prev)):
                    # keep remove previous_records[cursor_prev_bak] for len(cluster_prec) times
                    if previous_records[cursor_prev_bak]["operator"] == cluster_now[i]["operator"]:
                        previous_records.remove(previous_records[cursor_prev_bak])
                        # no need to cursor_prev_bak += 1 since the next record will come to the same place
                    else:
                        # unexpected behavior, warning
                        print(f"Warning: oprator name not matching, {previous_records[cursor_prev_bak]['operator']} vs {cluster_now[i]['operator']}")
                        previous_records.remove(previous_records[cursor_prev_bak])
                # recover cursor_prev so that it points to the next record
                cursor_prev = cursor_prev_bak
            else:
                # unexpected behavior, warning
                print(f"Warning: records length not matching, {len(cluster_now)} vs {len(cluster_prev)}, keep the longer one")
                if len(cluster_now) > len(cluster_prev):
                    # keep the new records
                    for i in range(len(cluster_prev)):
                        previous_records.remove(previous_records[cursor_prev_bak])
                        # recover cursor_prev so that it points to the next record
                        cursor_prev = cursor_prev_bak
                else:
                    # keep the previous records
                    for i in range(len(cluster_now)):
                        records.remove(records[cursor_now_bak])
                        # recover cursor_now so that it points to the next record
                        cursor_now = cursor_now_bak
                break
        else: # Time not matching, recover cursor_prev so that cursor_now can chase up
            cursor_prev = cursor_prev_bak

# merge the records
records += previous_records

# write to json
import json
with open("visit_records.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=4)
print(f"{len(records)-len(previous_records)} records found, merged into visit_records.json")

