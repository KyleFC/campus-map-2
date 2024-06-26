import json
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date, parse_time
from myapi.models import Course, Session

class Command(BaseCommand):
    help = 'Load a list of courses from a JSON file into the database'
    
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON file path containing the data')

    def handle(self, *args, **options):
        json_file = options['json_file']
        with open(json_file, 'r') as file:
            data = json.load(file)
            for entry in data:
                # Create the Course object
                course = Course.objects.create(
                    crn=entry.get('CRN'),
                    course_code=entry.get('Course'),
                    title=entry.get('Title'),
                    professor=entry.get('Professor'),
                    fees=entry.get('Fees') if entry.get('Fees') else None,
                    comments=entry.get('Comments') if entry.get('Comments') else None,
                    #meetday = entry.get('Meetday', '')[0],
                    start_date=entry.get('Start_Date')[0],  # Assumes start_date is a list
                    end_date=entry.get('End_Date')[0]  # Assumes end_date is a list
                )

                # Iterate through each session assuming meetday, start_time, end_time, location are lists
                meetdays = entry.get('Meetday', [])
                start_dates = entry.get('Start_Date', [])
                end_dates = entry.get('End_Date', [])
                start_times = entry.get('Start_Time', [])
                end_times = entry.get('End_Time', [])
                locations = entry.get('Location', [])

                num_sessions = len(meetdays)
                for i in range(num_sessions):
                    session = Session.objects.create(
                        course=course,
                        start_date=start_dates[i] if i < len(start_dates) else None,
                        end_date=end_dates[i] if i < len(end_dates) else None,
                        meetday=meetdays[i] if i < len(meetdays) else None,
                        start_time=start_times[i] if i < len(start_times) else None,
                        end_time=end_times[i] if i < len(end_times) else None,
                        location=locations[i] if i < len(locations) else None,
                    )
                    session.save()

                course.save()

    
        self.stdout.write(self.style.SUCCESS('Successfully loaded courses'))
