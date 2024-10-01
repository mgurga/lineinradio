from datetime import datetime, timedelta

from django.db import models

from website.models import Episode


class Slot(models.Model):
    datetime = models.DateTimeField()
    important = models.BooleanField(default=False)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    @property
    def is_playing(self) -> bool:
        end_time = self.datetime + timedelta(seconds=self.episode.length)
        return self.datetime <= datetime.now() < end_time

    def __str__(self) -> str:
        return f"{"!!! " if self.important else ""}{self.episode} @ {self.datetime.time()}"


class Schedule(models.Model):
    date = models.DateField()
    slots = models.ManyToManyField(Slot)

    @property
    def night_slots(self) -> [Slot]:
        out = []
        for slot in self.slots.all():
            if int(slot.datetime.strftime("%H")) <= 5:
                out.append(slot)
        return out

    @property
    def morning_slots(self) -> [Slot]:
        out = []
        for slot in self.slots.all():
            if 5 < int(slot.datetime.strftime("%H")) <= 11:
                out.append(slot)
        return out

    @property
    def afternoon_slots(self) -> [Slot]:
        out = []
        for slot in self.slots.all():
            if 11 < int(slot.datetime.strftime("%H")) <= 17:
                out.append(slot)
        return out

    @property
    def evening_slots(self) -> [Slot]:
        out = []
        for slot in self.slots.all():
            if 17 < int(slot.datetime.strftime("%H")):
                out.append(slot)
        return out

    @property
    def current_bloc_name(self) -> str:
        dtnh = datetime.now().hour
        if dtnh <= 5:
            return "night bloc (00:00 - 06:00)"
        elif 5 < dtnh <= 11:
            return "morning bloc (06:00 - 12:00)"
        elif 11 < dtnh <= 17:
            return "afternoon bloc (12:00 - 18:00)"
        else:
            return "evening bloc (18:00 - 24:00)"

    @property
    def current_slots(self) -> [Slot]:
        dtnh = datetime.now().hour
        if dtnh <= 5:
            return self.night_slots
        elif 5 < dtnh <= 11:
            return self.morning_slots
        elif 11 < dtnh <= 17:
            return self.afternoon_slots
        else:
            return self.evening_slots

    def __str__(self) -> str:
        return f"Schedule for {self.date.strftime("%b %d %Y")} ({self.slots.all().count()} slots)"
