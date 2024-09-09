import math
import os
import threading
import time as ptime
from datetime import datetime, time, timedelta

from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings

from scheduler.models import Schedule, Slot


class RadioConsumer(WebsocketConsumer):
    def file_iterator(self, file_path, chunk_size=8192, offset=0, length=None):
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

    def time_since_start(self, slot: Slot):
        if slot is None:
            return 0
        out = datetime.now() - slot.datetime
        return out.total_seconds()

    def get_current_slot(self):
        def add_time(t, secs):
            temp_datetime = datetime(2000, 1, 1, hour=t.hour, minute=t.minute, second=t.second)
            temp_datetime += timedelta(seconds=secs)
            if temp_datetime.day == 2:
                return time(hour=23, minute=59)
            else:
                return temp_datetime.time()

        if Schedule.objects.filter(date=datetime.now().date()).exists():
            schedule = Schedule.objects.filter(date=datetime.now().date())[0]
        else:
            return None

        dtslots = list(schedule.slots.order_by("datetime"))
        for s in dtslots:
            t = datetime.now().time()
            if s.datetime.time() <= t and t < add_time(s.datetime.time(), s.episode.length):
                return s

        # print(f"playing: {playing.episode.name}")

    def stream_bytes(self):
        sec_chunks = 1

        while self.send_chunks:
            ptime.sleep(sec_chunks)
            playing_slot = self.get_current_slot()
            if playing_slot is None:
                audio_path = str(settings.MEDIA_ROOT / "sfx" / "radiostatic.mp3")
            else:
                audio_path = str(playing_slot.episode.audiofile.path)

            # all audio is 128 kbps so each second is 16 KB
            # https://www.audiomountain.com/tech/audio-file-size.html
            chunk = 16 * 1024 * sec_chunks
            byte_point = math.floor(self.time_since_start(playing_slot)) * chunk
            first_byte = byte_point
            length = chunk
            b = self.file_iterator(audio_path, offset=first_byte, length=length)

            self.send(bytes_data=b)

    def connect(self):
        self.accept()
        self.send_chunks = True

        self.thread = threading.Thread(target=self.stream_bytes)
        self.thread.start()

    def receive(self, text_data=None, bytes_data=None):
        print(f"radio receieved data: {text_data}")
        self.send(text_data=text_data)

    def disconnect(self, code):
        print("radio disconnected")
        self.send_chunks = False
        raise StopConsumer()
