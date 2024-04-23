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
    courses = []
    course_info = []
    
    with open(text_file, 'r', encoding='utf-8') as f:
        for line in f:
            text = line.strip()
            #Find CRN to start new entry
            if (re.match("\d{5}", text) or text[0:7] == "Meetday") and (course_info[0][0:7] == "Meetday" or course_info[0][0:6] == "202430" or course_info[0][0:6] == 'Master'):
                course_info = []
            elif (re.match("\d{5}", text) or text[0:7] == "Meetday"):
                courses.append(' '.join(course_info))
                course_info = []

            course_info.append(text)
    return courses

# Precompile regex patterns
DATE_PATTERN = re.compile(r'(?P<Start_Date>\d{2}/\d{2}/\d{4})\s+-\s+(?P<End_Date>\d{2}/\d{2}/\d{4})')
TIME_PATTERN = re.compile(r'(?P<Start_Time>\d{1,2}:\d{2}\s+[AP]M)\s+-\s+(?P<End_Time>\d{1,2}:\d{2}\s+[AP]M)')
COURSE_PATTERN = re.compile(
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
ADDITIONAL_PATTERN = re.compile(
    r'(?P<Start_End_Dates>\d{2}/\d{2}/\d{4}\s+-\s+\d{2}/\d{2}/\d{4})\s+'
    r'(?P<Meetday>[MTWRFSU]*)\s*'
    r'(?:(?P<Times>By Arrangement|\d+:\d+\s+[AP]M\s+-\s+\d+:\d+\s+[AP]M))\s+'
    r'(?P<Location>[A-Za-z0-9-]+)'
)

def parse_dates_and_times(course_info):
    """Parse and split dates and times from course info, then store in lists."""
    # Handle Dates
    date_matches = DATE_PATTERN.search(course_info['Start_End_Dates'])
    if date_matches:
        course_info['Start_Date'] = date_matches.group('Start_Date')
        course_info['End_Date'] = date_matches.group('End_Date')
        del course_info['Start_End_Dates']  # Clean up the original date field

    # Handle Times
    if 'Times' in course_info and course_info['Times'] != 'By Arrangement':
        time_matches = TIME_PATTERN.search(course_info['Times'])
        if time_matches:
            course_info['Start_Time'] = time_matches.group('Start_Time')
            course_info['End_Time'] = time_matches.group('End_Time')
            del course_info['Times']  # Clean up the original time field
    elif course_info['Times'] == 'By Arrangement':
        course_info['Start_Time'] = 'By Arrangement'
        course_info['End_Time'] = 'By Arrangement'
        del course_info['Times']

def parse_course_line(line):
    match = COURSE_PATTERN.search(line)
    if not match:
        return None  # Early exit if line does not match the pattern

    course_info = match.groupdict()
    parse_dates_and_times(course_info)  # Parse initial session data

    remaining_text = line[match.end():].strip()
    course_info['Start_Date'] = [course_info['Start_Date']]
    course_info['End_Date'] = [course_info['End_Date']]
    course_info['Start_Time'] = [course_info['Start_Time']]
    course_info['End_Time'] = [course_info['End_Time']]
    course_info['Location'] = [course_info['Location']]
    course_info['Meetday'] = [course_info['Meetday']]
    
    if remaining_text:
        additional_info = ADDITIONAL_PATTERN.finditer(remaining_text)
        for additional_match in additional_info:
            additional_sessions = additional_match.groupdict()
            parse_dates_and_times(additional_sessions)  # Parse additional session data
            course_info['Start_Date'].append(additional_sessions['Start_Date'])
            course_info['End_Date'].append(additional_sessions['End_Date'])
            course_info['Start_Time'].append(additional_sessions['Start_Time'])
            course_info['End_Time'].append(additional_sessions['End_Time'])
            course_info['Location'].append(additional_sessions['Location'])
            course_info['Meetday'].append(additional_sessions['Meetday'])



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
    #BMC 070, 054, 151, 160

