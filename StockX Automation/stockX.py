import os
import time
import json
import logging
import psutil
import pickle
import pyautogui
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
webdriver_path = "undetected_chromedriver.exe"
url = input("Enter the product url: ")
size = input("Size:  ")
# url = 'https://stockx.com/timberland-6-inch-premium-waterproof-wheat'
# size = '5.5'

# Set up Chrome options
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)


# Initialize Chrome driver
driver = uc.Chrome( options=options)

def navigate_to_product_page(driver):
    """
    Navigate to the product page, handling any errors or bot verification challenges.
    """
    while True:
        try:
            logger.info(f"Navigating to product page")
            driver.get(url + "?defaultBid=false")
            logger.info("Page found.")
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
    """
    Determine the bid price based on the current ask price.
    """
    try:
        ask_price = driver.find_element(By.CSS_SELECTOR, "h2[data-testid='trade-box-buy-amount']").text
        ask_price = ''.join([c for c in ask_price if c.isdigit() or c == '.'])
        return int(ask_price) * 0.7
    except:
        logger.info("Visiting bidding page to determine bid price...")
        visit_bidding_page(driver, url, size)


def get_last_sale_price(driver, url, size):
    """
    Retrieve the last sale price for the product.
    """
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
    """
    Navigate to the bidding page for the product.
    """
    url = url.replace('stockx.com', 'stockx.com/buy')
    url += "?size=" + size
    try:
        logger.info(f"Navigating to bidding page")
        driver.get(url)
        # Check for bot verification
        logger.info("Checking for bot verification on bidding page...")
        # check_bot(driver)
        logger.info("Page found.")
    except TimeoutException as e:
        logger.error("Page not found: %s", e)
        driver.quit()
        exit()


def place_bid(driver, price_text):
    """
    Place a bid on the product.
    """
    try:
        time.sleep(5)
        logger.info("Waiting for bid input field to be present...")
        bid = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input.chakra-input"))
        )
        bid.send_keys(Keys.CONTROL + "a")
        bid.send_keys(Keys.DELETE)
        bid.send_keys(price_text)
        time.sleep(5)
    except:
        logger.error("Option for inputting Bid price not found, Quitting program")
        driver.quit()
        exit()
   
    try:
        logger.info("Checking for 'Review Bid' or 'Next' button...")
        # Locate the 'Review Bid' button
        review = driver.find_element(By.XPATH, "//*[text()='Review Bid']")
    except:
        try:
            # If 'Review Bid' is not found, locate the 'Next' button
            logger.info("Review Bid button not found, checking for 'Next' button...")
            review = driver.find_element(By.XPATH, "//*[text()='Next']")
        except TimeoutException as e:
            logger.error("Neither 'Review Bid' nor 'Next' button was found: %s", e)
            driver.quit()
            exit()

    try:
        review.click()
        time.sleep(5)
    except Exception as e:
        logger.error("Failed to click the button: %s", e)
        driver.quit()
        exit()


    try:
        time.sleep(5)
        logger.info("Waiting for 'Confirm Bid' button to be present...")
        confirm = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//*[text()='Confirm Bid']"))
        )
        confirm.click()
        logger.info("Bid placed successfully.")
        time.sleep(5)

    except TimeoutException as e:
        logger.error("Confirm Bid button not found: %s", e)
        driver.quit()
        exit()

def click_and_hold():
    button_location = pyautogui.locateCenterOnScreen("C:\\Users\\NeXbit\\Desktop\\Selenium\\StockX Automation\\button.png")
    if button_location:
        pyautogui.moveTo(button_location)
        pyautogui.mouseDown()
        time.sleep(15)
        pyautogui.mouseUp()

def main():
    try:
        logger.info("Navigating to product page...")
        navigate_to_product_page(driver)
        logger.info("Retrieving last sale price...")
        last_sale_price = get_last_sale_price(driver, url, size)
        logger.info("Visiting bidding page...")
        visit_bidding_page(driver, url, size)
        logger.info("Placing bid...")
        place_bid(driver, last_sale_price)
    except Exception as e:
        logger.error("An error occurred: %s", e)
    finally:
        driver.quit()
if __name__ == "__main__":
    main()