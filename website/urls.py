from django.conf import settings
from django.conf.urls.static import static
from django.templatetags.static import static as st
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

favicon_view = RedirectView.as_view(url=st("favicon.ico"), permanent=True)

urlpatterns = [
    path("favicon.ico", favicon_view),
    path("", views.index_page, name="index"),
    path("about", views.about_page, name="about"),
    path("login", views.login_page, name="login"),
    path("register", views.register_page, name="register"),
    path("settings", views.settings_page, name="settings"),
    path("logout", views.logout_page, name="logout"),
    path("customizer", views.customizer_page, name="customizer"),
    path("createshow", views.create_show_page, name="create show"),
    path("createepisode", views.create_episode_page, name="create episode"),
    path("djs", views.djs_page, name="djs page"),
    path("shows", views.shows_page, name="shows page"),
    path("dj/<str:username>", views.profile_page, name="profile"),
    path("editshow/<int:showid>", views.edit_show_page, name="edit show"),
    path("show/<int:showid>", views.show_page, name="view show"),
    path("editepisode/<int:episodeid>", views.edit_episode_page, name="edit episode"),
    path("deleteshow/<int:showid>", views.delete_show_page, name="delete show"),
    path("deleteepisode/<int:episodeid>", views.delete_episode_page, name="delete episode"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
