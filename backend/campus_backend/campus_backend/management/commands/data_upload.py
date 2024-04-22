import json
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date, parse_time
from myapi.models import Course, Session

class Command(BaseCommand):
    help = 'Load a list of courses from a JSON file into the database'
    
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON file path containing the data')

    def handle(self, *args, **options):
        with open('courses.json', 'r') as file:
            data = json.load(file)
            for entry in data:
                course = Course.objects.create(
                    course_code=entry.get('course_code', None),
                    title=entry.get('title', None),
                    professor=entry.get('professor', None),
                    fees=entry.get('fees', None),
                    comments=entry.get('comments', None),
                    start_date=parse_date(entry.get('start_date', None)),
                    end_date=parse_date(entry.get('end_date', None))
                )

                session = Session.objects.create(
                    course=course,
                    meetday=entry.get('meetday', None),
                    start_time=parse_time(entry.get('start_time', None)),
                    end_time=parse_time(entry.get('end_time', None)),
                    location=entry.get('location', None),
                    enrolled=entry.get('enrolled', None),
                    max_capacity=entry.get('max_capacity', None)
                )
                course.save()
                session.save()
    
        self.stdout.write(self.style.SUCCESS('Successfully loaded courses'))
