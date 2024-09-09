from datetime import datetime

from django.shortcuts import render

from .models import Schedule
from .tasks import download_bloc, generate_schedule


def schedule_page(request):
    if Schedule.objects.filter(date=datetime.now().date()).exists():
        schedule = Schedule.objects.filter(date=datetime.now().date())[0]
    else:
        schedule = generate_schedule()
        download_bloc()

    return render(request, "schedule.html", {"sch": schedule})
