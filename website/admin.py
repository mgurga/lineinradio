from django.contrib import admin

from .models import DJ, Episode, Show, Theme

admin.site.register(DJ)
admin.site.register(Show)
admin.site.register(Episode)
admin.site.register(Theme)
