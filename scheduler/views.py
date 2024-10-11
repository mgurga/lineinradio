import json
from datetime import datetime

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render

from website.models import DJ, Episode, Show

from .models import Schedule, Slot
from .tasks import generate_schedule, get_schedule


def schedule_page(request):
    schedule = get_schedule()
    return render(request, "schedule.html", {"sch": schedule})


@user_passes_test(lambda u: u.is_staff, login_url="/login")
def schedule_redir(request):
    return redirect(f"/scheduleeditor/{datetime.now().date()}")


@user_passes_test(lambda u: u.is_staff, login_url="/login")
def schedule_editor_page(request, date):
    if request.method == "POST":
        res = json.loads(request.body)

        if res["action"] == "deleteschedule":
            print(f"deleteing schedule for {date}")

            if Schedule.objects.filter(date=date).exists():
                Schedule.objects.filter(date=date).first().delete()

        elif res["action"] == "generateschedule":
            print(f"generating schedule for {date}")

            if not Schedule.objects.filter(date=date).exists():
                generate_schedule(date=datetime.strptime(date, "%Y-%m-%d"))

        elif res["action"] == "updateschedule":
            print(f"updating schedule for {date}")

            if Schedule.objects.filter(date=date).exists():
                Schedule.objects.filter(date=date).first().delete()

            newsch = Schedule.objects.create(date=datetime.strptime(date, "%Y-%m-%d"))

            for slotjson in res["schedule"]:
                nuser = User.objects.get(username=slotjson["creator"])
                ndj = DJ.objects.get(user=nuser)
                nshow = Show.objects.get(creator=ndj, name=slotjson["show"])
                nep = Episode.objects.get(show=nshow, name=slotjson["name"])
                ndt = datetime.strptime(slotjson["time"], "%Y-%m-%dT%H:%M:%S")

                nslot = Slot.objects.create(
                    datetime=ndt,
                    important=slotjson["important"],
                    episode=nep,
                )
                newsch.slots.add(nslot)

        return HttpResponse(status=200)
    else:
        if Schedule.objects.filter(date=date).exists():
            schedule = Schedule.objects.filter(date=date).first()
        else:
            schedule = None

        eps = Episode.objects.all()
        eps_dict = []
        for ep in eps:
            eps_dict.append(
                {
                    "name": ep.name,
                    "show": ep.show.name,
                    "length": ep.length,
                    "creator": ep.show.creator.handle,
                }
            )

        ctx = {"sch": schedule, "eps_json": json.dumps(eps_dict), "urldate": date}
        return render(request, "scheduleeditor.html", ctx)
