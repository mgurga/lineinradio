from django.urls import path

from . import views

urlpatterns = [path("schedule", views.schedule_page, name="schedule page")]
