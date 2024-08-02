from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import time

driver = webdriver.Chrome()
driver.get("https://www.youtube.com")


WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CLASS_NAME, "ytd-searchbox-spt"))
)

input_element = driver.find_element(By.XPATH, '//*[@id="search"]')
input_element.send_keys("Memory Reboot" + Keys.RETURN)

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Memory Reboot")) 
)
link = driver.find_element(By.PARTIAL_LINK_TEXT, "Memory Reboot")
link.click()

time.sleep(180)
driver.quit()