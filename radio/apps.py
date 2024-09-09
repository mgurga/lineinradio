from django.apps import AppConfig

byte_chunk = bytes()
last_chunk_update = None


class RadioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "radio"

    def ready(self):
        global byte_chunk
        global last_chunk_update
