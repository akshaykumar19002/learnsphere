from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Create periodic tasks'

    def handle(self, *args, **kwargs):
        # Create schedule to run every day
        schedule, created = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)

        # Link the schedule to your task
        PeriodicTask.objects.get_or_create(
            interval=schedule, 
            name='Reccomendation task for Added courses', 
            task='dashboard.tasks.generate_recommendations_for_added_courses'
        )

        # Link the schedule to your task
        PeriodicTask.objects.get_or_create(
            interval=schedule, 
            name='Reccomendation task for User preferences', 
            task='dashboard.tasks.generate_recommendations_for_user_prefs'
        )
        