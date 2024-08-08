import os
import time
import json
import logging
import psutil
import pickle
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kill any existing Chrome driver processes
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if 'chrome' in proc.info['name']:
            proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

EMAIL = "kamranbangash@nexbit.pk"
PASSWORD = "Kamran123."
COOKIES_FILE = "cookies.pkl"
webdriver_path = "chromedriver.exe"

# url = input("Enter the product url: ")
# size = input("Size:  ")
url = 'https://stockx.com/timberland-6-inch-premium-waterproof-wheat'
size = '5.5'
# Set up Chrome options
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")

# Initialize Chrome driver
driver = uc.Chrome(executable_path=webdriver_path, options=options)

# Define the cookies file
# cookies_file = "cookies.json"


def save_cookies(driver):
    cookies = driver.get_cookies()
    pickle.dump(cookies, open("cookies.pkl", "wb"))

# Function to load cookies
def load_cookies(driver):
    cookies = pickle.load(open("cookies.pkl", "rb"))    
    for cookie in cookies:
        cookie['domain'] = '.stockx.com'
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(e)


def check_cookies(driver):
    if os.path.isfile("cookies.pkl"):
        load_cookies(driver)
        driver.refresh()
        logger.info("Loaded cookies.")
        return
    else:
        login_to_stockx(driver, EMAIL, PASSWORD)


def login_to_stockx(driver, email, password):
    driver.get('https://stockx.com/login')
    check_bot(driver)
    try:
        time.sleep(5)
        email = driver.find_element(By.ID, "email-login")
        email.send_keys(EMAIL + Keys.TAB)

        password = driver.find_element(By.ID, "password-login")
        password.send_keys(PASSWORD + Keys.RETURN)
        time.sleep(5)
        # save_cookies(driver)
        check_bot(driver)
        logger.info("Logged in successfully.")
    except TimeoutException as e:
        logger.error("Login failed: %s", e)
        login_to_stockx(driver, email, password)
        raise 

def navigate_to_product_page(driver):
    while True:
        try:
            driver.get(url + "?defaultBid=false")
            logger.info("Page found.")
            check_bot(driver)
            break
        except Exception as e:
            logger.error("Page not found: %s", e)
            cont = input("Enter Y to try another URL and N to quit: ").strip().lower()
            if cont == 'n':
                driver.quit()
                logger.info("Exiting the program.")
                exit()
            elif cont != 'y':
                logger.warning("Invalid input. Please enter 'y' or 'n'.")

def bid_price(driver, url, size):
    try:
        ask_price = driver.find_element(By.CSS_SELECTOR, "h2[data-testid='trade-box-buy-amount']").text
        ask_price = ''.join([c for c in ask_price if c.isdigit() or c == '.'])
        return int(ask_price) * 0.7
    except:
        visit_bidding_page(driver, url, size)

def get_last_sale_price(driver, url, size):
    time.sleep(5)
    try:
        last_sale_element = driver.find_element(By.CSS_SELECTOR, 'div[data-component="LastSale"]')
        price_text = last_sale_element.find_elements(By.CSS_SELECTOR, 'p')[1].text
        price_text = ''.join([c for c in price_text if c.isdigit() or c == '.'])
        if not price_text:
            raise
        price_text = str(int(price_text) + 1)
        return price_text
    except:
        logger.error("Last sale Amount not Available, Entering Custom price")
        price_text = bid_price(driver, url, size)
        return price_text

def visit_bidding_page(driver, url, size):
    url = url.replace('stockx.com', 'stockx.com/buy')
    url += "?size=" + size
    try:
        driver.get(url)
        check_bot(driver)
        logger.info("Page found.")
    except TimeoutException as e:
        logger.error("Page not found: %s", e)
        driver.quit()
        exit()
    

def place_bid(driver, price_text):
    
    try:
        time.sleep(5)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.chakra-input"))
        )
        bid = driver.find_element(By.CSS_SELECTOR, "input.chakra-input")
        bid.send_keys(Keys.CONTROL + "a")
        bid.send_keys(Keys.DELETE)
        bid.send_keys(price_text)
        time.sleep(5)
    except:
        print("Option for inputting Bid price not found, Quitting program")
        driver.quit()
        exit()


    try:
        review = driver.find_element(By.XPATH, "//*[text()='Review Bid']")
        review.click()
        time.sleep(5)
    except TimeoutException as e:
        logger.error("Review Bid button not found: %s", e)
        driver.quit()
        exit()

    try:
        time.sleep(5)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Confirm Bid']"))
        )
        confirm = driver.find_element(By.XPATH, "//*[text()='Confirm Bid']")
        confirm.click()
        logger.info("Bid placed successfully.")
    except TimeoutException as e:
        logger.error("Confirm Bid button not found: %s", e)
        driver.quit()
        exit()
    
    # time.sleep(5)
    # WebDriverWait(driver, 5).until(
    #     EC.presence_of_element_located((By.XPATH, "//*[text()='Confirm Bid']"))
    # )
    # confirm = driver.find_element(By.XPATH, "//*[text()='Confirm Bid']")
    # confirm.click()

def check_bot(driver):
    try:
        hold = driver.find_element(By.XPATH, "//*[text()='Press & Hold']")
        actions = ActionChains(driver)
        actions.click_and_hold(hold).perform()
        time.sleep(5)
    except:
        pass

def main():
    try:
        # check_cookies(driver)
        login_to_stockx(driver, EMAIL, PASSWORD)
        navigate_to_product_page(driver)
        last_sale_price = get_last_sale_price(driver, url, size)
        visit_bidding_page(driver, url, size)
        place_bid(driver, last_sale_price)
    except Exception as e:
        logger.error("An error occurred: %s", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()