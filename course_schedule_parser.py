import fitz
import re
import json

def extract_text_line_by_line(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []

    for page in doc:
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda block: (block[1], block[0]))
        for block in blocks:
            text_blocks.append(block[4])
    text = ''.join(text_blocks)

    with open('extracted_text.txt', 'w', encoding='utf-8') as file:
        file.write(text)

    return text

def parse_courses(text_file):
    courses = []  # List to hold all course entries
    course_info = []  # Temporary storage for accumulating lines of a single course
    
    with open(text_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Check if the line contains a CRN (5-digit number) indicating the start of a course entry
            text = line.strip()

            if (re.match("\d{5}", text) or text[0:7] == "Meetday") and (course_info[0][0:7] == "Meetday" or course_info[0][0:6] == "202430" or course_info[0][0:6] == 'Master'):
                course_info = []
            elif (re.match("\d{5}", text) or text[0:7] == "Meetday"):
                courses.append(' '.join(course_info))
                course_info = []

            course_info.append(text)
    return courses

def parse_course_line(line):
    pattern = re.compile(
        r'(?P<CRN>\d{5})\s+'
        r'(?P<Course>[A-Za-z]+-[A-Z0-9]+-(?:[A-Za-z0-9]+))\s+'
        r'(?P<Title>[A-Z&-:/\s\(\)]+(?:\s+\([A-Za-z\s]+\))?)\s+'
        r'(?P<Professor>(?:STAFF|[A-Za-z-\s\']+,\s+[A-Za-z]\.))\s+'
        r'(?:(?P<Waitlist>Y+))?\s*'
        r'(?:\$(?P<Fees>\d+))?\s*'
        r'(?:\s*(?P<Comments>[^\$]+?))?\s*'
        r'(?P<Start_End_Dates>\d{2}/\d{2}/\d{4}\s+-\s+\d{2}/\d{2}/\d{4})\s+'
        r'(?P<Meetday>[MTWRFSU]*)\s*'
        r'(?P<Times>(?:By Arrangement|\d+:\d+\s+[AP]M\s+-\s+\d+:\d+\s+[AP]M))\s+'
        r'(?P<Location>[A-Za-z0-9-]+)\s+'
        r'(?P<Units>\d+(?:\.\d+)?)\s+'
        r'(?P<Enrolled>\d+/\d+)'
    )
    match = pattern.search(line)
    if not match:
        return None

    course_info = match.groupdict()
   
    remaining_text = line[match.end():].strip()
    additional_sessions = []

    if remaining_text:
        additional_pattern = re.compile(
            r'(?P<Additional_Start_End_Dates>\d{2}/\d{2}/\d{4}\s+-\s+\d{2}/\d{2}/\d{4})\s+'
            r'(?P<Additional_Meetday>[MTWRFSU]*)\s*'
            r'(?:(?P<Additional_Times>By Arrangement|\d+:\d+\s+[AP]M\s+-\s+\d+:\d+\s+[AP]M))\s+'
            r'(?P<Additional_Location>[A-Za-z0-9-]+)'
        )

        for additional_match in additional_pattern.finditer(remaining_text):
            additional_sessions.append(additional_match.groupdict())

    if additional_sessions:
        course_info['Additional_Sessions'] = additional_sessions

    return course_info

def course_dict_to_json(course_dict):
    json_string = json.dumps(course_dict, indent=4)

    with open('courses.json', 'w') as json_file:
        json_file.write(json_string)

if __name__ == "__main__":
    #text = extract_text_line_by_line("MCS_UG_Spring_2024.pdf")
    text = 'extracted_text.txt'
    parsed = parse_courses(text)

    #Courses should be a dictionary of courses
    courses = []
    course = {}
    for i, line in enumerate(parsed):
        #print(line)
        courses.append(parse_course_line(line))
        print(line)
        
    course_dict_to_json(courses)
    #print(courses)
    #Structure of courses
    #CRN COURSE TITLE PROFESSOR WAITLIST FEES COMMENTS START_END_DATES MEETDAY TIMES LOCATION UNITS ENROLLED - (START_END_DATES MEETDAY TIMES LOCATION) optional and can repeat


