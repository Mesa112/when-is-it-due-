from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import getpass
import time
import re
import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Course:
    title: str
    course_code: str
    section: str
    crn: str  # Course Reference Number in brackets
    term: str
    lecture_type: str = "Lecture"
    college: str = "Queens College"
    status: str = "Open"
    url: Optional[str] = None
    
    def __str__(self):
        status_str = f" ({self.status})" if self.status != "Open" else ""
        return f"{self.title} - {self.course_code} {self.section} [{self.crn}]{status_str}"

def login_to_cuny():
    """Log in to CUNY Brightspace and return the driver."""
    driver = webdriver.Chrome()
    driver.maximize_window()  # Maximize to ensure all elements are visible
    
    try:
        # Navigate to the login page
        driver.get("https://brightspace.cuny.edu/")
        
        # Wait for the login form to appear
        wait = WebDriverWait(driver, 15)
        username_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[contains(text(), 'Username')]/following::input[1]")))
        
        password_input = driver.find_element(By.XPATH, "//label[contains(text(), 'Password')]/following::input[1]")
        
        # Get credentials
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")
        
        # Enter credentials
        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        
        # Wait for login to complete
        time.sleep(5)
        
        # Take a screenshot after login
        os.makedirs("screenshots", exist_ok=True)
        driver.save_screenshot("screenshots/after_login.png")
        
        print(f"Logged in. Current URL: {driver.current_url}")
        return driver
        
    except Exception as e:
        print(f"Error during login: {str(e)}")
        driver.save_screenshot("screenshots/login_error.png")
        driver.quit()
        raise