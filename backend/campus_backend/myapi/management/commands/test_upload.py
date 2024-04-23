# Test if the upload works by querying the database .raw()

from django.core.management.base import BaseCommand
from myapi.models import Course

class Command(BaseCommand):
    help = 'Query the database for all courses'

    def handle(self, *args, **options):
        courses = Course.objects.raw('SELECT * FROM myapi_course')
        for course in courses:
            self.stdout.write(self.style.SUCCESS(f'{course.title} ({course.course_code}) - {course.professor}'))
            for session in course.sessions.all():
                self.stdout.write(self.style.SUCCESS(f'{session.course.course_code} - {session.location} on {session.meetday} from {session.start_time} to {session.end_time}'))
        self.stdout.write(self.style.SUCCESS('Successfully queried courses'))