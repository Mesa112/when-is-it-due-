from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import os

from portal_login import login_to_cuny
from scrape import navigate_to_courses_page, extract_course_info
from course_parser import parse_course_elements
from assignment_scraper import get_all_course_assignments

def main():
    driver = None
    try:
        print("Starting CUNY Brightspace course scraper...")
        
        # Login
        driver = login_to_cuny()
        
        # Navigate to courses page
        navigate_to_courses_page(driver)
        
        # Extract raw course information
        raw_courses = extract_course_info(driver)
        
        if not raw_courses:
            print("No course elements found.")
            return []
        
        # Parse into structured Course objects
        courses = parse_course_elements(raw_courses)
        
        # Display results
        if courses:
            print("\nCourses found:")
            for i, course in enumerate(courses, 1):
                print(f"{i}. {course}")
                if course.url:
                    print(f"   URL: {course.url}")
                print()
            
            print(f"Total courses found: {len(courses)}")
            
            # Get assignments for all courses
            print("\nFetching assignments for all courses...")
            all_assignments = get_all_course_assignments(driver, courses)
            
            # Display assignments
            if all_assignments:
                print("\nUpcoming assignments:")
                for i, assignment in enumerate(all_assignments, 1):
                    print(f"{i}. {assignment['title']} - {assignment['course_code']}")
                    print(f"   Due: {assignment['date']}")
                    if assignment.get('status'):
                        print(f"   Status: {assignment['status']}")
                    print()
                
                print(f"Total assignments found: {len(all_assignments)}")
            else:
                print("No assignments found.")
        else:
            print("No structured course data could be extracted.")
            
        return courses
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if driver:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            driver.save_screenshot("screenshots/error.png")
        return []
        
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()