from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import getpass
import time

#Start the browser to login
driver = webdriver.Chrome()
driver.get("https://brightspace.cuny.edu/d2l/home/7019")
# Locate input fields using XPath under the labels
username_input = driver.find_element(By.XPATH, "//label[contains(text(), 'Username')]/following::input[1]")
password_input = driver.find_element(By.XPATH, "//label[contains(text(), 'Password')]/following::input[1]")
while True:
    username_input.clear()
    password_input.clear()

    # Take user input
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    # Send informtion
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Submit form with Enter key
    password_input.send_keys(Keys.ENTER)

    time.sleep(10)
    try:
        error_box = driver.find_element(By.XPATH, "//*[contains(text(), 'invalid') or contains(text(), 'Incorrect') or contains(text(), 'Error'), or contains(text(), 'failed)]")
        print("❌ Login failed. Please try again.")
    except:
        print("✅ Login successful!")
        break
    time.sleep(3)



