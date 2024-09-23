from datetime import datetime

from django.core.management.base import BaseCommand
from django_q.tasks import Schedule as QSchedule


class Command(BaseCommand):
    help = "register tasks that run in the night, morning, afternoon, and evening"

    def handle(self, *args, **options):
        if not QSchedule.objects.filter(name="night duties").exists():
            QSchedule.objects.get_or_create(
                name="night duties",
                func="scheduler.tasks.night_duties",
                schedule_type=QSchedule.DAILY,
                repeats=-1,
                next_run=datetime.now().replace(hour=23, minute=30),
            )

        if not QSchedule.objects.filter(name="morning duties").exists():
            QSchedule.objects.get_or_create(
                name="morning duties",
                func="scheduler.tasks.morning_duties",
                schedule_type=QSchedule.DAILY,
                repeats=-1,
                next_run=datetime.now().replace(hour=5, minute=30),
            )

        if not QSchedule.objects.filter(name="afternoon duties").exists():
            QSchedule.objects.get_or_create(
                name="afternoon duties",
                func="scheduler.tasks.afternoon_duties",
                schedule_type=QSchedule.DAILY,
                repeats=-1,
                next_run=datetime.now().replace(hour=11, minute=30),
            )

        if not QSchedule.objects.filter(name="evening duties").exists():
            QSchedule.objects.get_or_create(
                name="evening duties",
                func="scheduler.tasks.evening_duties",
                schedule_type=QSchedule.DAILY,
                repeats=-1,
                next_run=datetime.now().replace(hour=17, minute=30),
            )

        if not QSchedule.objects.filter(name="crossover duties").exists():
            QSchedule.objects.get_or_create(
                name="crossover duties",
                func="scheduler.tasks.crossover_duties",
                schedule_type=QSchedule.DAILY,
                repeats=-1,
                next_run=datetime.now().replace(hour=0, minute=1),
            )

        print("Successfully registered tasks")
