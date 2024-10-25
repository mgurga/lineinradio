import math
import os
from datetime import datetime, time, timedelta

from django.conf import settings
from django_q.tasks import Schedule as QSchedule

import scheduler
from scheduler.models import Slot

from .apps import byte_chunk, last_chunk_update


def generate_mpd_queue():
    sch = scheduler.tasks.get_schedule()
    mpcp = f"mpc -P {settings.MPD_PASSWORD}"

    os.system(f"{mpcp} update")
    os.system(f"{mpcp} clear")

    for islot in sch.important_slots:
        audio_exists = islot.episode.audiofile.name is not None
        islot_end_time = datetime.combine(datetime.now().date(), islot.datetime.time())
        islot_end_time += timedelta(seconds=islot.episode.length)
        print(f"islot: {islot}")

        if islot.is_playing and audio_exists:
            print(f"force playing important slot: {islot}")
            # add only important slot and play
            os.system(f"{mpcp} add {os.path.basename(islot.episode.audiofile.name)}")
            os.system(f"{mpcp} play")

            curseek = datetime.now()
            curseek -= datetime.combine(datetime.now().date(), islot.datetime.time())
            curseek = curseek - timedelta(microseconds=curseek.microseconds)
            print(f"seeking to {curseek}")
            os.system(f"{mpcp} seekthrough +{curseek}")

            # recreate mpd queue when important slot is over
            QSchedule.objects.get_or_create(
                name=f"{islot} ending",
                func="radio.tasks.generate_mpd_queue",
                schedule_type=QSchedule.ONCE,
                repeats=-1,  # this will delete after running
                next_run=islot_end_time,
            )
            return None
        elif islot.datetime.time() > datetime.now().time():
            # create task to overwrite mpd queue when important slot is present
            QSchedule.objects.get_or_create(
                name=f"{islot} reminder",
                func="radio.tasks.generate_mpd_queue",
                schedule_type=QSchedule.ONCE,
                repeats=-1,  # this will delete after running
                next_run=datetime.combine(datetime.now().date(), islot.datetime.time()),
            )

    for slot in sch.slots.all():
        if not slot.important and slot.episode.audiofile.name is not None:
            os.system(f"{mpcp} add {os.path.basename(slot.episode.audiofile.name)}")

    t = datetime.now()
    os.system(f"{mpcp} play")
    print(f"seeking to {t.strftime("%H:%M:%S")}")
    os.system(f"{mpcp} seekthrough +{t.strftime("%H:%M:%S")}")


def file_iterator(file_path, chunk_size=8192, offset=0, length=None):
    out = bytearray()
    with open(file_path, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            # yield data
            for b in data:
                out.append(b)
    return bytes(out)


def time_since_start(slot: Slot):
    if slot is None:
        return 0
    out = datetime.now() - slot.datetime
    return out.total_seconds()


def get_current_slot():
    def add_time(t, secs):
        temp_datetime = datetime(2000, 1, 1, hour=t.hour, minute=t.minute, second=t.second)
        temp_datetime += timedelta(seconds=secs)
        if temp_datetime.day == 2:
            return time(hour=23, minute=59)
        else:
            return temp_datetime.time()

    schedule = scheduler.tasks.get_schedule()

    dtslots = list(schedule.slots.order_by("datetime"))
    current_slots = []
    for s in dtslots:
        t = datetime.now().time()
        if s.datetime.time() <= t and t < add_time(s.datetime.time(), s.episode.length):
            current_slots.append(s)

    for s in current_slots:
        if s.important:
            return s

    return current_slots[0]

    # print(f"playing: {playing.episode.name}")


def get_stream_bytes(sec_chunks=1):
    global last_chunk_update
    global byte_chunk

    if last_chunk_update is None:
        last_chunk_update = datetime.now() - timedelta(days=1)

    if (datetime.now() - last_chunk_update).total_seconds() < sec_chunks:
        return byte_chunk
    else:
        playing_slot = get_current_slot()
        if playing_slot is None:
            audio_path = str(settings.MEDIA_ROOT / "sfx" / "radiostatic.mp3")
        else:
            audio_path = str(playing_slot.episode.audiofile.path)

        # all audio is 128 kbps so each second is 16 KB
        # https://www.audiomountain.com/tech/audio-file-size.html
        chunk = 16 * 1024 * sec_chunks
        byte_point = math.floor(time_since_start(playing_slot)) * chunk
        first_byte = byte_point
        length = chunk
        b = file_iterator(audio_path, offset=first_byte, length=length)

        last_chunk_update = datetime.now()
        byte_chunk = b
        return b
