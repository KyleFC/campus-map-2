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
                    course_code=entry.get('course_code'),
                    title=entry.get('title'),
                    professor=entry.get('professor'),
                    fees=entry.get('fees'),
                    comments=entry.get('comments'),
                    start_date=parse_date(entry['start_date'][0]),  # Assumes start_date is a list
                    end_date=parse_date(entry['end_date'][0])  # Assumes end_date is a list
                )

                # Iterate through each session assuming meetday, start_time, end_time, location are lists
                meetdays = entry.get('meetday', [])
                start_times = entry.get('start_time', [])
                end_times = entry.get('end_time', [])
                locations = entry.get('location', [])
                enrolled = entry.get('enrolled', 0)  # Assumes a single value for enrolled, not list-based

                num_sessions = len(meetdays)
                for i in range(num_sessions):
                    session = Session.objects.create(
                        course=course,
                        meetday=meetdays[i] if i < len(meetdays) else None,
                        start_time=parse_time(start_times[i]) if i < len(start_times) else None,
                        end_time=parse_time(end_times[i]) if i < len(end_times) else None,
                        location=locations[i] if i < len(locations) else None,
                        enrolled=enrolled
                    )
                    session.save()

                course.save()

    
        self.stdout.write(self.style.SUCCESS('Successfully loaded courses'))
