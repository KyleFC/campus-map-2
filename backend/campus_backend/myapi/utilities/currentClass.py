import json
import datetime


def time_to_datetime(time):
    hour, minute = time.split(':')
    minute, period = minute.split(' ')
    hour = int(hour)
    minute = int(minute)

    if period == 'PM' and hour != 12:
        hour += 12
    elif period == 'AM' and hour == 12:
        hour = 0

    return datetime.datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

def find_current_classes(courses, input_day, input_time):
    current_classes = []

    def is_course_at_time(course_day, course_times, input_day, input_time):
        if input_day not in course_day:
            return False
        if course_times == "TBA" or course_times == "By Arrangement":
            return False
        start_time_str, end_time_str = course_times.split(' - ')
        start_time = time_to_datetime(start_time_str)
        end_time = time_to_datetime(end_time_str)
        input_datetime = time_to_datetime(input_time)

        return start_time <= input_datetime <= end_time

    for course in courses:
        if is_course_at_time(course['Meetday'], course['Times'], input_day, input_time):
            current_classes.append(course)

    return current_classes
if __name__ == '__main__':
    with open('C:/Users/epicb/Projects/Campus-Map/campus-map/backend/campus_backend/myapi/data/courses.json') as file:
        courses = json.load(file)

    current_classes = find_current_classes(courses, "M", "7:00 PM")

    print("Current classes at the given time:")
    for course in current_classes:
        print(f"Class name: {course['Title']}\nProfessor: {course['Professor']}\nTime: {course['Times']}\nLocation: {course['Location']}\n")
