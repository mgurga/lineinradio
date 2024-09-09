from django.contrib.auth.models import User
from django.db import models


class Theme(models.Model):
    background = models.CharField(max_length=10, default="#222222")
    primary = models.CharField(max_length=10, default="#c2681e")
    accent = models.CharField(max_length=10, default="#111111")
    text = models.CharField(max_length=10, default="#ffffff")
    secondary_text = models.CharField(max_length=10, default="#cccccc")


# DO NOT USE
def get_default_theme():
    return Theme.objects.create().id


class DJ(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    is_verified = models.BooleanField(default=False)
    # profile pictures are 200x200
    profile_pic = models.ImageField(upload_to="profilepics", default="/profilepics/default.png")
    bio = models.TextField(default="working on something big")
    profile_theme = models.ForeignKey(Theme, on_delete=models.CASCADE)

    def set_display_name(self, name: str):
        self.user.first_name = name
        self.user.save()

    @property
    def display_name(self):
        if self.user.first_name == "":
            return self.user.username
        else:
            return self.user.first_name

    def set_pronouns(self, pronouns: str):
        self.user.last_name = pronouns
        self.user.save()

    @property
    def pronouns(self):
        return self.user.last_name

    def set_handle(self, handle: str):
        if User.objects.filter(username=handle).exists():
            return "username already in use"

        self.user.username = handle
        self.user.save()

    @property
    def handle(self):
        return self.user.username

    def __str__(self):
        return self.user.username


class Show(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="my new show")
    one_shot = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(DJ, on_delete=models.CASCADE)

    show_theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    # banners are 800x200
    banner = models.ImageField(upload_to="showbanners", default="/showbanners/defaultbanner.png")

    def __str__(self):
        return self.name


class Episode(models.Model):
    name = models.CharField(max_length=100)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField(default=0)  # in seconds
    description = models.TextField(default="my new episode")

    link = models.URLField()
    audiofile = models.FileField(upload_to="episodes", null=True, blank=True)

    all_blocs = models.BooleanField(default=True)
    night_bloc = models.BooleanField(default=False)
    morning_bloc = models.BooleanField(default=False)
    afternoon_bloc = models.BooleanField(default=False)
    evening_bloc = models.BooleanField(default=False)
