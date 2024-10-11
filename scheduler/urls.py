from django.urls import path

from . import views

urlpatterns = [
    path("schedule", views.schedule_page, name="schedule page"),
    path("scheduleeditor", views.schedule_redir, name="schedule editor redirect"),
    path("scheduleeditor/<str:date>", views.schedule_editor_page, name="schedule editor page"),
]
