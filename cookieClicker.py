import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

driver.get("https://orteil.dashnet.org/cookieclicker/")

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.ID, "langSelect-EN"))
)
language = driver.find_element(By.ID, "langSelect-EN")
language.click()

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.ID, "bigCookie"))
)
cookie = driver.find_element(By.ID, "bigCookie")

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CLASS_NAME, "price"))
)

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.ID, "cookies"))
)
cookies = driver.find_element(By.ID, "cookies").text.split(" ")[0]

for i in range(100):
    cookie.click()
    print(cookies)

items = driver.find_elements(By.CLASS_NAME, "price")

