from datetime import datetime

from django.shortcuts import render

from .models import Schedule


def schedule_page(request):
    if Schedule.objects.filter(date=datetime.now().date()).exists():
        schedule = Schedule.objects.filter(date=datetime.now().date())[0]

    return render(request, "schedule.html", {"sch": schedule})
