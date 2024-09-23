import os
from datetime import datetime, time, timedelta
from multiprocessing import Process

import yt_dlp
from django.conf import settings
from django.core.files import File

import radio.tasks
from website.models import Episode

from .models import Schedule, Slot


def generate_schedule(date=datetime.now().date()) -> Schedule:  # noqa: B008
    def add_time(t, secs):
        temp_datetime = datetime(2000, 1, 1, hour=t.hour, minute=t.minute, second=t.second)
        temp_datetime += timedelta(seconds=secs)
        if temp_datetime.day == 2:
            return time(hour=0, minute=0)
        else:
            return temp_datetime.time()

    # delete all schedules date unless it contains an important slot
    # schdate = Schedule.objects.filter(date=date)
    # if schdate.exists():
    #     if schdate.count() != 1:
    #         for sch in schdate:
    #             for slot in sch.slots.all():
    #                 slot.delete()
    #     else:
    #         if schdate[0].slots.filter(important=True).count == 0:
    #             for sch in schdate[0]:
    #                 for slot in sch.slots.all():
    #                     slot.delete()

    planned_time = time(0, 0)
    used_eps = []

    # create night bloc schedule
    night_slots = []
    possible_night_eps = list(Episode.objects.filter(night_bloc=True).order_by("?"))

    while int(planned_time.strftime("%H")) <= 5:
        ep = possible_night_eps.pop()
        while ep in used_eps:
            ep = possible_night_eps.pop()
        used_eps.append(ep)

        planned_datetime = datetime.combine(date, planned_time)
        night_slots.append(Slot.objects.create(datetime=planned_datetime, episode=ep))
        planned_time = add_time(planned_time, ep.length)

    # create morning bloc schedule
    morning_slots = []
    possible_morning_eps = list(Episode.objects.filter(morning_bloc=True).order_by("?"))

    while int(planned_time.strftime("%H")) <= 11:
        ep = possible_morning_eps.pop()
        while ep in used_eps:
            ep = possible_morning_eps.pop()
        used_eps.append(ep)

        planned_datetime = datetime.combine(date, planned_time)
        morning_slots.append(Slot.objects.create(datetime=planned_datetime, episode=ep))
        planned_time = add_time(planned_time, ep.length)

    # create afternoon bloc schedule
    afternoon_slots = []
    possible_afternoon_eps = list(Episode.objects.filter(afternoon_bloc=True).order_by("?"))

    while int(planned_time.strftime("%H")) <= 17:
        ep = possible_afternoon_eps.pop()
        while ep in used_eps:
            ep = possible_afternoon_eps.pop()
        used_eps.append(ep)
        planned_datetime = datetime.combine(date, planned_time)
        afternoon_slots.append(Slot.objects.create(datetime=planned_datetime, episode=ep))
        planned_time = add_time(planned_time, ep.length)

    # create evening bloc schedule
    evening_slots = []
    possible_evening_eps = list(Episode.objects.filter(evening_bloc=True).order_by("?"))

    used_eps.clear()  # clear now because not enough episodes

    while int(planned_time.strftime("%H")) != 0:
        ep = possible_evening_eps.pop()
        while ep in used_eps:
            ep = possible_evening_eps.pop()

        used_eps.append(ep)
        planned_datetime = datetime.combine(date, planned_time)
        evening_slots.append(Slot.objects.create(datetime=planned_datetime, episode=ep))
        planned_time = add_time(planned_time, ep.length)

    # roll all blocs into one schedule
    print(datetime.now())
    sch = Schedule.objects.create(date=date)
    for slot in night_slots:
        sch.slots.add(slot)
    for slot in morning_slots:
        sch.slots.add(slot)
    for slot in afternoon_slots:
        sch.slots.add(slot)
    for slot in evening_slots:
        sch.slots.add(slot)

    return sch


def download_slot(slot: Slot):
    file_exists = slot.episode.audiofile.storage.exists(slot.episode.audiofile.name)
    if slot.episode.audiofile.name and file_exists:
        print(f"{slot.episode.show.name} - {slot.episode.name} already downloaded")
        return

    url = slot.episode.link

    dlpath = str(settings.MEDIA_ROOT / "downloads" / "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "mp3/bestaudio",
        "outtmpl": dlpath,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        outpath = ydl.prepare_filename(info)

        filename = outpath.split(os.sep)[-1]
        f = open(settings.MEDIA_ROOT / "downloads" / filename, "rb")
        slot.episode.audiofile.save(filename, File(f), save=True)
        os.remove(settings.MEDIA_ROOT / "downloads" / filename)


def download_slots(sl: [Slot]):
    try:
        plist = []
        for slot in sl:
            download_slot(slot)
            plist.append(Process(target=download_slot, args=(slot,)))

        for p in plist:
            p.start()
    except AssertionError:
        for s in sl:
            download_slot(s)


def download_bloc():
    hour = datetime.now().time().hour

    schedule = get_schedule()

    if hour <= 5:
        slots_to_download = schedule.night_slots
    elif 5 < hour <= 11:
        slots_to_download = schedule.morning_slots
    elif 11 < hour <= 17:
        slots_to_download = schedule.afternoon_slots
    elif 17 < hour:
        slots_to_download = schedule.evening_slots

    download_slots(slots_to_download)


def get_schedule(d=datetime.now().date()) -> Schedule:  # noqa: B008
    if Schedule.objects.filter(date=d).exists():
        return Schedule.objects.filter(date=d).first()
    else:
        s = generate_schedule(date=d)
        download_bloc()
        return s


def crossover_duties():
    """
    This runs in the morning at 12:01 am, it does the following:
    - clears the current mpd queue
    - add all songs for the day in the queue
    """

    sl = []
    for slot in get_schedule().slots.all():
        sl.append(slot)
    download_slots(sl)

    radio.tasks.generate_mpd_queue()


def night_duties():
    """
    This runs every night at 11:30 pm, it does the following:
    - generate schedule for tomorrow
    - download night bloc for tomorrow
    - cleanup episodes that played throughout the day
    """
    print("running night duties...")

    tmr = datetime.now().date() + timedelta(days=1)
    schedule_tmr = get_schedule(tmr)

    tmr_slots = []
    for s in schedule_tmr.slots.all():
        tmr_slots.append(s)
    download_slots(tmr_slots)

    # todo cleanup episodes


def morning_duties():
    """
    This runs every morning at 5:30 am, it does the following:
    - download morning bloc
    - cleanup episodes
    """
    print("running morning duties...")

    schedule = get_schedule()
    download_slots(schedule.morning_slots)

    # todo cleanup episodes


def afternoon_duties():
    """
    This runs every afternoon at 11:30 am, it does the following:
    - download afternoon bloc
    - cleanup episodes
    """
    print("running afternoon duties...")

    schedule = get_schedule()
    download_slots(schedule.afternoon_slots)

    # todo cleanup episodes


def evening_duties():
    """
    This runs every evening at 5:30 pm, it does the following:
    - download evening bloc
    - cleanup episodes
    """
    print("running evening duties...")

    schedule = get_schedule()
    download_slots(schedule.evening_slots)

    # todo cleanup episodes
