# these imports help us validate that the installation was correct
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

# instantiate the driver
driver = webdriver.Firefox()
# opens google
print("opening google...")
driver.get("https://www.google.com/")
input("Accept the terms of service, them press any key in this terminal...")
# types a query
print("searching for our course...")
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("Chalmers Applied object-oriented programming")
search_box.submit()
time.sleep(10)
# clicks on the first result
input("Press any key in this terminal to close...")
driver.quit()
