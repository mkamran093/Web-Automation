import os
import time
import json
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

# Initialize Chrome driver
driver = uc.Chrome()

# Define the cookies file
cookies_file = "cookies.json"

# Function to save cookies
def save_cookies(driver, file_path):
    with open(file_path, "w") as file:
        json.dump(driver.get_cookies(), file)

# Function to load cookies
def load_cookies(driver, file_path):
    with open(file_path, "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

# Navigate to the login page
driver.get('https://stockx.com/')

# Load cookies if they exist
if os.path.exists(cookies_file):
    load_cookies(driver, cookies_file)
    driver.refresh()

# Check if login is required by checking for the login element
try:
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "nav-login"))
    )
    login = driver.find_element(By.ID, "nav-login")
    login.click()

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "email-login"))
    )

    email = driver.find_element(By.ID, "email-login")
    email.send_keys(os.getenv("EMAIL") + Keys.TAB)

    password = driver.find_element(By.ID, "password-login")
    password.send_keys(os.getenv("PASSWORD") + Keys.RETURN)

    # Save cookies after logging in
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "some-element-id-after-login")))
    save_cookies(driver, cookies_file)
except Exception as e:
    print("Already logged in or login not required",e)

# Navigate to the desired page
try:
    driver.get(os.getenv("URL"))
    print("Page found")
except:
    print("Page not found")
    driver.quit()

# Find the last sale element
try:
    last_sale_element = driver.find_element(By.CSS_SELECTOR, 'div[data-component="LastSale"]')
    price_text = last_sale_element.find_elements(By.CSS_SELECTOR, 'p')[1].text
    print(price_text)

    # Click the "Place Bid" button
    bid_Btn = driver.find_element(By.XPATH, "//*[text()='Place Bid']")
    bid_Btn.click()

    time.sleep(10)

    # Select the size
    size = os.getenv("SIZE")
    xpath_expression = f"//button[.//span[text()='{size}']]"
    sizeBtn = driver.find_element(By.XPATH, xpath_expression)
    sizeBtn.click()

    # Enter the bid amount
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.chakra-input"))
    )
    bid = driver.find_element(By.CSS_SELECTOR, "input.chakra-input")
    bid.clear()
    bid.send_keys(price_text)

    # Click the "Next" button to place the bid
    place_bid = driver.find_element(By.XPATH, "//*[text()='Next']")
    place_bid.click()

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()
