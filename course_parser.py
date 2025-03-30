import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class Course:
    title: str
    course_code: str
    section: str = ""
    crn: str = ""  # Course Reference Number in brackets
    term: str = "Spring 2025"
    lecture_type: str = "Lecture"
    college: str = "Queens College"
    status: str = "Open"
    url: Optional[str] = None
    
    def __str__(self):
        status_str = f" ({self.status})" if self.status != "Open" else ""
        section_str = f" {self.section}" if self.section else ""
        crn_str = f" [{self.crn}]" if self.crn else ""
        return f"{self.title} - {self.course_code}{section_str}{crn_str}{status_str}"

def parse_course_elements(course_elements: List[Dict[str, Any]]) -> List[Course]:
    """Convert raw course elements into structured Course objects."""
    courses = []
    
    # Debug: Print all raw elements
    print("\nRaw course elements found:")
    for i, element in enumerate(course_elements, 1):
        text = element.get("text", "").strip().replace('\n', ' ')
        print(f"Element {i}: {text[:100]}...")
    
    for element in course_elements:
        text = element.get("text", "").strip()
        url = element.get("href")
        
        # Skip empty texts
        if not text:
            continue
            
        # Clean up text (replace multiple spaces, newlines)
        text = re.sub(r'\s+', ' ', text)
        
        # Skip very short texts that aren't likely courses
        if len(text) < 15:
            continue
        
        # Debug
        print(f"\nProcessing text: {text[:100]}...")
        
        # Check if course is closed
        status = "Closed" if "Closed" in text else "Open"
        
        # Try multiple patterns to extract course info
        
        # Look for CSCI course code pattern
        course_code_match = re.search(r'CSCI (\d+(/\d+)?)', text)
        if course_code_match:
            print(f"Found CSCI course code: {course_code_match.group(0)}")
            course_code = course_code_match.group(0)
            
            # Try to extract CRN
            crn_match = re.search(r'\[(\d{5})\]', text)
            crn = crn_match.group(1) if crn_match else ""
            
            # Try to extract section
            section_match = re.search(r'CSCI \d+(/\d+)? (\d{3})', text)
            section = section_match.group(2) if section_match else ""
            
            # Try to extract title based on SP pattern
            sp_title_match = re.search(r'SP \[\w+\] (.*?) CSCI', text)
            if sp_title_match:
                title = sp_title_match.group(1).strip()
            else:
                # Try alternative title pattern with dash
                dash_title_match = re.search(r'CSCI \d+(/\d+)? - (.*?)( \(|,)', text)
                if dash_title_match:
                    title = dash_title_match.group(2).strip()
                else:
                    # Last resort - try to find a meaningful title
                    title_candidates = [
                        "Principles of Programming Lang",
                        "VT: Special Topics in Comp Sci",
                        "Deep Learning",
                        "Digital Image Processing",
                        "Software Engineering"
                    ]
                    
                    title = "Unknown Course"
                    for candidate in title_candidates:
                        if candidate in text:
                            title = candidate
                            break
            
            courses.append(Course(
                title=title,
                course_code=course_code,
                section=section,
                crn=crn,
                status=status,
                url=url
            ))
            print(f"Added course: {title} - {course_code} {section} [{crn}]")
    
    # Check for specific known courses that might have been missed
    course_indicators = [
        ("Principles of Programming", "CSCI 316"),
        ("Special Topics", "CSCI 381"),
        ("Deep Learning", "CSCI 381/780"),
        ("Digital Image Processing", "CSCI 367"),
        ("Software Engineering", "CSCI 370")
    ]
    
    # Check if any known courses are missing
    for indicator, code in course_indicators:
        found = False
        for course in courses:
            if indicator in course.title or code in course.course_code:
                found = True
                break
        
        if not found:
            # Check raw elements for this course
            for element in course_elements:
                text = element.get("text", "").strip()
                if indicator in text and code in text:
                    print(f"Found missing course: {indicator} - {code}")
                    
                    # Extract what info we can
                    crn_match = re.search(r'\[(\d{5})\]', text)
                    crn = crn_match.group(1) if crn_match else ""
                    
                    section_match = re.search(r'{} (\d{{3}})'.format(code.split('/')[0]), text)
                    section = section_match.group(1) if section_match else ""
                    
                    courses.append(Course(
                        title=indicator,
                        course_code=code,
                        section=section,
                        crn=crn,
                        status="Closed" if "Closed" in text else "Open",
                        url=element.get("href")
                    ))
                    break
    
    return courses