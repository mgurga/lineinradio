from django.shortcuts import render

from .tasks import get_schedule


def schedule_page(request):
    schedule = get_schedule()
    return render(request, "schedule.html", {"sch": schedule})
