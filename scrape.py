from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import re
import os
from portal_login import login_to_cuny  



def navigate_to_courses_page(driver):
    """Navigate to the courses page."""
    try:
        # Check if we need to go to the courses page
        if "/d2l/home" in driver.current_url:
            # We're already on a home page
            print("Already on a home page. Checking for course tabs...")
            
            # First try to click on the "2025 Spring Term" tab if it exists
            try:
                # Try multiple selectors for the Spring Term tab
                tab_selectors = [
                    "//button[contains(text(), '2025 Spring Term')]",
                    "//div[contains(text(), '2025 Spring Term') and @role='tab']",
                    "//button[contains(@class, 'tab') and contains(text(), 'Spring')]"
                ]
                
                for selector in tab_selectors:
                    try:
                        tabs = driver.find_elements(By.XPATH, selector)
                        if tabs:
                            tabs[0].click()
                            print(f"Clicked on '2025 Spring Term' tab using selector: {selector}")
                            time.sleep(3)
                            break
                    except:
                        continue
                
                if not any(tabs := driver.find_elements(By.XPATH, tab) for tab in tab_selectors):
                    print("Could not find '2025 Spring Term' tab")
                    
                    # Try using JavaScript to find and click the tab
                    found_tab = driver.execute_script("""
                        const tabs = Array.from(document.querySelectorAll('button, div[role="tab"]'));
                        for (const tab of tabs) {
                            if (tab.textContent.includes('Spring Term')) {
                                tab.click();
                                return true;
                            }
                        }
                        return false;
                    """)
                    
                    if found_tab:
                        print("Clicked on Spring Term tab using JavaScript")
                        time.sleep(3)
            except Exception as e:
                print(f"Error clicking tab: {str(e)}")
                print("Could not find or click '2025 Spring Term' tab")
        else:
            # Navigate to the courses page
            print("Navigating to courses page...")
            driver.get("https://brightspace.cuny.edu/d2l/home")
            time.sleep(5)
            
            # Try clicking on the Spring Term tab
            try:
                spring_tabs = driver.find_elements(By.XPATH, "//button[contains(text(), '2025 Spring Term')]")
                if spring_tabs:
                    spring_tabs[0].click()
                    print("Clicked on '2025 Spring Term' tab")
                    time.sleep(3)
            except:
                print("Could not find or click '2025 Spring Term' tab")
        
        # Try to directly click on course cards if they're visible
        try:
            course_cards = driver.find_elements(By.XPATH, 
                "//div[contains(text(), 'CSCI') or .//div[contains(text(), 'CSCI')]]//ancestor::div[contains(@class, 'card') or contains(@class, 'tile')]")
            
            if course_cards:
                print(f"Found {len(course_cards)} visible course cards")
                
                # Get current window handle to keep track of main window
                main_window = driver.current_window_handle
                
                # For each course card, try to click it and get the URL
                for i, card in enumerate(course_cards):
                    try:
                        card_text = card.text.strip()
                        if "CSCI" in card_text:
                            print(f"Attempting to click course card: {card_text[:50]}...")
                            
                            # Try to find and click a link in the card
                            links = card.find_elements(By.TAG_NAME, "a")
                            if links:
                                # Open in new tab by middle-clicking
                                ActionChains(driver).key_down(Keys.COMMAND).click(links[0]).key_up(Keys.COMMAND).perform()
                                time.sleep(2)
                                
                                # Switch to new tab and get URL
                                new_window = [window for window in driver.window_handles if window != main_window][-1]
                                driver.switch_to.window(new_window)
                                
                                course_url = driver.current_url
                                print(f"Course URL: {course_url}")
                                
                                # Take a screenshot of the course page
                                driver.save_screenshot(f"screenshots/course_{i+1}.png")
                                
                                # Close tab and switch back to main window
                                driver.close()
                                driver.switch_to.window(main_window)
                    except Exception as e:
                        print(f"Error clicking course card: {str(e)}")
                        # Make sure we're back in the main window
                        driver.switch_to.window(main_window)
        except Exception as e:
            print(f"Error processing course cards: {str(e)}")
        
        # Take a screenshot of the courses page
        driver.save_screenshot("screenshots/courses_page.png")
        
    except Exception as e:
        print(f"Error navigating to courses page: {str(e)}")
        driver.save_screenshot("screenshots/navigation_error.png")

def extract_course_info(driver):
    """Extract course information by directly targeting the course card elements based on their content."""
    print("Extracting course information...")
    courses = []
    
    try:
        # Take a screenshot before extraction
        driver.save_screenshot("screenshots/before_extraction.png")
        
        # First approach: Try to find the course cards
        course_cards = driver.find_elements(By.CSS_SELECTOR, 
            "div[class*='card'], div[class*='tile'], div[class*='course']")
        
        print(f"Found {len(course_cards)} potential course cards")
        
        # If we found some cards, process them
        for card in course_cards:
            try:
                card_text = card.text.strip()
                if not card_text or len(card_text) < 10:
                    continue
                
                # Look for CSCI courses
                if "CSCI" in card_text:
                    # Try to find a link in this card
                    links = card.find_elements(By.TAG_NAME, "a")
                    course_url = None
                    
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "/d2l/home/" in href and "/d2l/home/7019" not in href:
                            course_url = href
                            print(f"Found course URL: {course_url} for card text: {card_text[:50]}...")
                            break
                    
                    courses.append({
                        "text": card_text,
                        "element_type": "card",
                        "href": course_url
                    })
            except Exception as e:
                print(f"Error processing card: {str(e)}")
        
        # If we couldn't find course URLs through cards, try a more direct approach
        if not any(course.get("href") for course in courses):
            print("Trying to find courses directly...")
            
            # Navigate to the 'All Courses' page if possible
            try:
                all_courses_link = driver.find_element(By.XPATH, "//a[contains(text(), 'View All Courses')]")
                all_courses_link.click()
                print("Clicked 'View All Courses' link")
                time.sleep(3)
                driver.save_screenshot("screenshots/all_courses_page.png")
            except:
                # If "View All Courses" link isn't found, try navigating directly
                print("'View All Courses' link not found, navigating directly...")
                driver.get("https://brightspace.cuny.edu/d2l/home/all")
                time.sleep(3)
            
            # Now try to find all course links on this page
            course_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/d2l/home/']")
            print(f"Found {len(course_links)} course links on All Courses page")
            
            for link in course_links:
                href = link.get_attribute("href")
                
                # Skip the main homepage
                if not href or "/d2l/home/7019" in href:
                    continue
                
                text = link.text.strip()
                if not text:
                    parent = link.find_element(By.XPATH, "./..")
                    text = parent.text.strip()
                
                if text and "CSCI" in text:
                    print(f"Found course link: {href} for text: {text[:50]}...")
                    courses.append({
                        "text": text,
                        "element_type": "link",
                        "href": href
                    })
        
        # If we still don't have course URLs, let's try using the search function
        if not any(course.get("href") for course in courses):
            print("Trying course search...")
            
            # First navigate to a page with a search bar
            driver.get("https://brightspace.cuny.edu/d2l/home")
            time.sleep(3)
            
            # Try to find the search box
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
                
                # For each course we've found, try to search for it
                for course in courses:
                    course_code = None
                    
                    # Extract the course code (e.g., "CSCI 316")
                    code_match = re.search(r'CSCI \d+(/\d+)?', course.get("text", ""))
                    if code_match:
                        course_code = code_match.group(0)
                    
                    if course_code:
                        print(f"Searching for course: {course_code}")
                        
                        # Clear the search box and enter the course code
                        search_box.clear()
                        search_box.send_keys(course_code)
                        search_box.send_keys(Keys.RETURN)
                        time.sleep(3)
                        
                        # Try to find course links in the search results
                        result_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/d2l/home/']")
                        for link in result_links:
                            href = link.get_attribute("href")
                            if href and "/d2l/home/7019" not in href:
                                course["href"] = href
                                print(f"Found URL for {course_code}: {href}")
                                break
                        
                        # Go back to the home page for the next search
                        driver.get("https://brightspace.cuny.edu/d2l/home")
                        time.sleep(2)
                        search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
            except Exception as e:
                print(f"Error during course search: {str(e)}")
        
        # One last approach - try to construct URLs based on known patterns
        known_course_pages = {}
        
        # Check screenshots to see if we can find any course-specific elements
        for image_path in ["screenshots/courses_page.png", "screenshots/after_login.png", "screenshots/all_courses_page.png"]:
            if os.path.exists(image_path):
                print(f"Using screenshot {image_path} to search for course patterns...")
                # We're just noting that these screenshots might have useful info
        
        # Filter and deduplicate courses
        filtered_courses = []
        seen_texts = set()
        
        for course in courses:
            # Clean up and normalize the text
            text = course.get("text", "").strip()
            if not text or len(text) < 10:
                continue
                
            # Skip duplicates
            normalized_text = re.sub(r'\s+', ' ', text).lower()
            normalized_text = re.sub(r'\[.*?\]', '', normalized_text)  # Remove anything in brackets
            normalized_text = ' '.join(normalized_text.split()[:5])  # Just use first few words
            
            if normalized_text in seen_texts:
                continue
                
            seen_texts.add(normalized_text)
            filtered_courses.append(course)
        
        print(f"Found {len(filtered_courses)} unique courses")
        
        # Debug output
        print("\nFinal course list:")
        for i, course in enumerate(filtered_courses, 1):
            text = course.get("text", "").strip()
            href = course.get("href", "No URL")
            print(f"{i}. {text[:50]}... - URL: {href}")
        
        return filtered_courses
        
    except Exception as e:
        print(f"Error extracting course information: {str(e)}")
        driver.save_screenshot("screenshots/extraction_error.png")
        return []