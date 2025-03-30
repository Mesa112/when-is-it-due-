from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import re
import datetime
from typing import List, Dict, Any, Optional

def navigate_to_course_assignments(driver, course_url):
    """Navigate to the assignments page for a specific course."""
    try:
        # Navigate to the course page
        print(f"Navigating to course: {course_url}")
        driver.get(course_url)
        time.sleep(3)
        
        # Take a screenshot of the course page
        driver.save_screenshot("screenshots/course_page.png")
        
        # Find and click on the Assignments tab
        try:
            assignments_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Assignments')]"))
            )
            assignments_tab.click()
            print("Clicked on 'Assignments' tab")
            time.sleep(3)
            
            # Take a screenshot of the assignments page
            driver.save_screenshot("screenshots/assignments_page.png")
            return True
            
        except Exception as e:
            print(f"Error finding or clicking Assignments tab: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error navigating to course assignments: {str(e)}")
        return False

def extract_assignment_info(driver):
    """Extract information about assignments from the assignments page."""
    assignments = []
    
    try:
        # Wait for assignments table or list to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.d2l-table, div.d2l-le-assignment"))
        )
        
        # Try to find assignment elements - different Brightspace versions may have different structures
        assignment_elements = driver.find_elements(By.CSS_SELECTOR, 
            "tr.d2l-grid-row, div.d2l-le-assignment, d2l-le-assignment, d2l-activity-card")
        
        print(f"Found {len(assignment_elements)} potential assignment elements")
        
        if len(assignment_elements) == 0:
            # Try an alternative approach using JavaScript to find assignments
            assignments_data = driver.execute_script("""
                const results = [];
                
                // Look for common assignment indicators
                const assignmentTitles = Array.from(document.querySelectorAll('h3.d2l-heading, .d2l-le-text-title, a[href*="dropbox"]'));
                
                for (const title of assignmentTitles) {
                    // Find the closest container with date information
                    let container = title.closest('tr, div.d2l-le-assignment, d2l-activity-card');
                    if (!container) continue;
                    
                    // Extract title text
                    const titleText = title.textContent.trim();
                    
                    // Find date elements
                    let dateText = '';
                    const dateElements = container.querySelectorAll('.d2l-le-text-due-date, .d2l-dates, span[class*="date"]');
                    for (const dateEl of dateElements) {
                        if (dateEl.textContent.includes('Due') || dateEl.textContent.includes('End') || dateEl.textContent.includes('date')) {
                            dateText = dateEl.textContent.trim();
                            break;
                        }
                    }
                    
                    // Find status/completion information
                    let statusText = '';
                    const statusElements = container.querySelectorAll('.d2l-status, span[class*="status"], span[class*="completion"]');
                    if (statusElements.length > 0) {
                        statusText = statusElements[0].textContent.trim();
                    }
                    
                    // Get link to assignment
                    let assignmentLink = '';
                    if (title.tagName === 'A') {
                        assignmentLink = title.href;
                    } else {
                        const linkElement = container.querySelector('a[href*="dropbox"], a[href*="quiz"], a[href*="discuss"]');
                        if (linkElement) {
                            assignmentLink = linkElement.href;
                        }
                    }
                    
                    results.push({
                        title: titleText,
                        date: dateText,
                        status: statusText,
                        link: assignmentLink
                    });
                }
                
                return results;
            """)
            
            if assignments_data:
                assignments.extend(assignments_data)
        
        # Process assignment elements found via Selenium
        for element in assignment_elements:
            try:
                # Extract title
                title_element = element.find_element(By.CSS_SELECTOR, 
                    "h3, .d2l-le-text-title, a.d2l-link, .d2l-activity-name")
                title = title_element.text.strip()
                
                # Extract due date
                date_text = ""
                date_elements = element.find_elements(By.CSS_SELECTOR, 
                    ".d2l-le-text-due-date, .d2l-dates, span[class*='date']")
                
                for date_el in date_elements:
                    if "Due" in date_el.text or "End" in date_el.text:
                        date_text = date_el.text.strip()
                        break
                
                # Extract status
                status = ""
                status_elements = element.find_elements(By.CSS_SELECTOR, 
                    ".d2l-status, span[class*='status'], span[class*='completion']")
                
                if status_elements:
                    status = status_elements[0].text.strip()
                
                # Extract link
                link_elements = element.find_elements(By.CSS_SELECTOR, "a")
                link = link_elements[0].get_attribute("href") if link_elements else ""
                
                assignments.append({
                    "title": title,
                    "date": date_text,
                    "status": status,
                    "link": link
                })
                
            except Exception as e:
                print(f"Error processing assignment element: {str(e)}")
        
        # Filter out empty or incomplete assignments
        filtered_assignments = []
        for assignment in assignments:
            if assignment.get("title"):
                filtered_assignments.append(assignment)
        
        # Sort assignments by due date (if possible)
        try:
            def extract_date(assignment):
                date_text = assignment.get("date", "")
                if not date_text:
                    return datetime.datetime.max
                
                # Look for date patterns
                date_match = re.search(r'(\w{3})\s+(\d{1,2}),?\s+(\d{4})', date_text)
                if date_match:
                    try:
                        month, day, year = date_match.groups()
                        return datetime.datetime.strptime(f"{month} {day} {year}", "%b %d %Y")
                    except:
                        pass
                
                return datetime.datetime.max
            
            filtered_assignments.sort(key=extract_date)
        except:
            # If sorting fails, just leave them in original order
            pass
        
        return filtered_assignments
        
    except Exception as e:
        print(f"Error extracting assignment information: {str(e)}")
        driver.save_screenshot("screenshots/assignment_extraction_error.png")
        return []

def get_course_assignments(driver, course):
    """Get all assignments for a specific course."""
    try:
        # If the course has a URL, use it
        if course.url:
            course_url = course.url
        else:
            # If no URL, try to search for the course
            course_url = f"https://brightspace.cuny.edu/d2l/home"  # Default fallback
            print(f"No URL for course: {course.title}. Using default.")
        
        # Navigate to the assignments page
        if navigate_to_course_assignments(driver, course_url):
            # Extract assignment information
            assignments = extract_assignment_info(driver)
            
            print(f"Found {len(assignments)} assignments for course: {course.title}")
            return assignments
        else:
            print(f"Could not navigate to assignments for course: {course.title}")
            return []
            
    except Exception as e:
        print(f"Error getting assignments for course {course.title}: {str(e)}")
        return []

def get_all_course_assignments(driver, courses):
    """Get assignments for all courses."""
    all_assignments = []
    
    for course in courses:
        print(f"\nProcessing assignments for: {course.title}")
        
        # Get assignments for this course
        course_assignments = get_course_assignments(driver, course)
        
        # Add course information to each assignment
        for assignment in course_assignments:
            assignment["course"] = course.title
            assignment["course_code"] = course.course_code
            all_assignments.append(assignment)
    
    # Sort all assignments by due date
    try:
        def extract_date(assignment):
            date_text = assignment.get("date", "")
            if not date_text:
                return datetime.datetime.max
            
            # Look for date patterns
            date_match = re.search(r'(\w{3})\s+(\d{1,2}),?\s+(\d{4})', date_text)
            if date_match:
                try:
                    month, day, year = date_match.groups()
                    return datetime.datetime.strptime(f"{month} {day} {year}", "%b %d %Y")
                except:
                    pass
            
            return datetime.datetime.max
        
        all_assignments.sort(key=extract_date)
    except:
        # If sorting fails, just leave them in original order
        pass
    
    return all_assignments