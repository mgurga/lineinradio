import yt_dlp
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions
from django.shortcuts import redirect, render

from scheduler.tasks import get_schedule

from .forms import (
    CreateEpisodeForm,
    CreateShowForm,
    PasswordChangeForm,
    UserForm,
    UsernameChangeForm,
)
from .models import DJ, Episode, Show, Theme


def index_page(request):
    schedule = get_schedule()
    return render(request, "index.html", {"sch": schedule})


def about_page(request):
    return render(request, "about.html")


def djs_page(request):
    djs = DJ.objects.filter(is_verified=True)
    return render(request, "djs.html", {"djs": djs})


def shows_page(request):
    shows = Show.objects.all()
    return render(request, "shows.html", {"shows": shows})


def show_page(request, showid):
    try:
        show = Show.objects.get(id=showid)
    except Show.DoesNotExist:
        return render(request, "noblank.html", {"thing": "show"})

    episodes = Episode.objects.filter(show=show).order_by("-created")

    return render(request, "show.html", {"show": show, "episodes": episodes})


@login_required(login_url="/")
def logout_page(request):
    logout(request)
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/")
def delete_show_page(request, showid):
    try:
        show = Show.objects.get(id=showid)
        if show.creator is not request.user.dj:
            pass

        Episode.objects.filter(show=show).delete()
        show.show_theme.delete()
        show.delete()
    except Show.DoesNotExist:
        pass

    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/")
def delete_episode_page(request, episodeid):
    try:
        ep = Episode.objects.get(id=episodeid)
        if ep.show.creator is not request.user.dj:
            pass

        ep.delete()
    except Episode.DoesNotExist:
        pass

    return redirect(request.META.get("HTTP_REFERER"))


def profile_page(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "noblank.html", {"thing": "dj"})

    shows = Show.objects.filter(creator=user.dj)
    episodes = []
    for show in shows:
        for ep in Episode.objects.filter(show=show):
            episodes.append(ep)

    ctx = {"dj": user.dj, "shows": shows, "episodes": episodes}
    return render(request, "profile.html", ctx)


def login_page(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(f"/dj/{username}")
        else:
            return redirect("/login#invalid")
    else:
        return render(request, "login.html", {})


def register_page(request):
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            new_dj = DJ.objects.create(user=user, profile_theme=Theme.objects.create())
            new_dj.save()
            return redirect("/login#success")
        else:
            return render(request, "register.html", {"user_form": user_form})
    else:
        user_form = UserForm()

    return render(request, "register.html", {"user_form": user_form})


@login_required(login_url="/login")
def settings_page(request):
    logged_dj = None if request.user.is_anonymous else request.user.dj
    if request.method == "POST":
        if "submituser" in request.POST:
            user_change_form = UsernameChangeForm(data=request.POST)
            if user_change_form.is_valid():
                logged_dj.user.username = request.POST["username"]
                logged_dj.user.save()
                ctx = {"logged_dj": logged_dj, "userchangeform": "success"}
                return render(request, "settings.html", ctx)
            else:
                ctx = {"logged_dj": logged_dj, "userchangeform": user_change_form}
                return render(request, "settings.html", ctx)
        elif "submitpass" in request.POST:
            pass_change_form = PasswordChangeForm(data=request.POST)
            if pass_change_form.is_valid():
                logged_dj.user.set_password(request.POST["password"])
                logged_dj.user.save()
                ctx = {"logged_dj": logged_dj, "passchangeform": "success"}
                return render(request, "settings.html", ctx)
            else:
                ctx = {"logged_dj": logged_dj, "passchangeform": pass_change_form}
                return render(request, "settings.html", ctx)
        else:
            logged_dj.user.delete()
            logged_dj.profile_theme.delete()
            logged_dj.delete()
            return redirect("/")

    else:
        return render(request, "settings.html", {"logged_dj": logged_dj})


@login_required(login_url="/login")
def customizer_page(request):
    logged_dj = None if request.user.is_anonymous else request.user.dj

    if request.method == "POST" and logged_dj.user.username == request.user.username:
        if request.FILES.get("pfp", False):
            w, h = get_image_dimensions(request.FILES["pfp"])
            if w > 200 or h > 200:
                print(f"pfp incorrect size recieved {w}x{h} image")
                return redirect("/customizer#failed")

            logged_dj.profile_pic = request.FILES["pfp"]

        if request.POST["displayname"]:
            logged_dj.set_display_name(request.POST["displayname"])

        if request.POST["bio"]:
            logged_dj.bio = request.POST["bio"]

        logged_dj.profile_theme.background = request.POST["bgcolor"]
        logged_dj.profile_theme.primary = request.POST["prcolor"]
        logged_dj.profile_theme.accent = request.POST["accolor"]
        logged_dj.profile_theme.text = request.POST["txcolor"]
        logged_dj.profile_theme.secondary_text = request.POST["stcolor"]
        logged_dj.profile_theme.save()

        logged_dj.save()
        return redirect(f"/dj/{logged_dj.user.username}")
    else:
        return render(request, "customizer.html", {"logged_dj": logged_dj})


@login_required(login_url="/login")
def create_show_page(request):
    logged_dj = None if request.user.is_anonymous else request.user.dj
    if logged_dj is None:
        return redirect("/")

    if not logged_dj.is_verified:
        return redirect(f"/dj/{request.user.dj.handle}#notverified")

    if request.method == "POST":
        create_show_form = CreateShowForm(data=request.POST)

        if create_show_form.is_valid():
            w, h = get_image_dimensions(request.FILES["banner"])
            if w > 800 or h > 200:
                return redirect("/createshow#incorrectbannersize")

            show = create_show_form.save(commit=False)
            show.creator = request.user.dj
            show.show_theme = Theme.objects.create()
            show.save()
    else:
        create_show_form = CreateShowForm()

    return render(request, "createshow.html", {"createshowform": create_show_form})


@login_required(login_url="/login")
def edit_show_page(request, showid):
    logged_dj = None if request.user.is_anonymous else request.user.dj
    if not logged_dj.is_verified:
        return redirect("/")

    try:
        show = Show.objects.get(id=showid)
    except Show.DoesNotExist:
        return render(request, "noblank.html", {"thing": "show"})

    if not show.creator == logged_dj:
        return redirect("/")

    if request.method == "POST":
        create_show_form = CreateShowForm(data=request.POST)

        if create_show_form.is_valid():
            if request.FILES.get("banner", False):
                newbanner = request.FILES["banner"]

                w, h = get_image_dimensions(newbanner)
                if w > 800 or h > 200:
                    return redirect(f"/editshow/{showid}#incorrectbannersize")
            else:
                newbanner = show.banner

            show.banner = newbanner
            show.name = request.POST["name"]
            show.description = request.POST["description"]
            show.save()

        return redirect(f"/dj/{request.user.dj.handle}")
    else:
        create_show_form = CreateShowForm()
        ctx = {"createshowform": create_show_form, "show": show}
        return render(request, "editshow.html", ctx)


def get_length(link) -> int:
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info.get("duration")


@login_required(login_url="/login")
def create_episode_page(request):
    logged_dj = None if request.user.is_anonymous else request.user.dj
    if not logged_dj.is_verified:
        return redirect("/")

    shows = Show.objects.filter(creator=request.user.dj)

    if request.method == "POST":
        create_episode_form = CreateEpisodeForm(data=request.POST)
        if create_episode_form.is_valid():
            ep_show = create_episode_form.save(commit=False).show
            episode = Episode.objects.create(
                name=request.POST["name"],
                show=ep_show,
                description=request.POST["description"],
                link=request.POST["link"],
                length=get_length(request.POST["link"]),
                all_blocs=False,
                night_bloc=True if request.POST.get("nightcb") else False,
                morning_bloc=True if request.POST.get("morningcb") else False,
                afternoon_bloc=True if request.POST.get("afternooncb") else False,
                evening_bloc=True if request.POST.get("eveningcb") else False,
            )
            episode.save()
        else:
            ctx = {"createepisodeform": create_episode_form, "shows": shows}
            return render(request, "createepisode.html", ctx)

        return redirect(f"/dj/{request.user.dj.handle}")
    else:
        create_episode_form = CreateEpisodeForm()
        ctx = {"logged_dj": logged_dj, "createepisodeform": create_episode_form, "shows": shows}
        return render(request, "createepisode.html", ctx)


@login_required(login_url="/login")
def edit_episode_page(request, episodeid):
    logged_dj = None if request.user.is_anonymous else request.user.dj
    if not logged_dj.is_verified:
        return redirect("/")

    shows = Show.objects.filter(creator=request.user.dj)

    try:
        ep = Episode.objects.get(id=episodeid)
    except Episode.DoesNotExist:
        return render(request, "noblank.html", {"thing": "episode"})

    if not ep.show.creator == logged_dj:
        return redirect("/")

    if request.method == "POST":
        create_episode_form = CreateEpisodeForm(data=request.POST)
        ep_show = create_episode_form.save(commit=False).show
        if create_episode_form.is_valid():
            ep.name = request.POST["name"]
            ep.show = ep_show
            ep.description = request.POST["description"]
            ep.link = request.POST["link"]
            ep.length = get_length(request.POST["link"])
            ep.night_bloc = True if request.POST.get("nightcb") else False
            ep.morning_bloc = True if request.POST.get("morningcb") else False
            ep.afternoon_bloc = True if request.POST.get("afternooncb") else False
            ep.evening_bloc = True if request.POST.get("eveningcb") else False
            ep.save()

        return redirect(f"/dj/{request.user.dj.handle}")
    else:
        create_episode_form = CreateEpisodeForm()
        ctx = {"createepisodeform": create_episode_form, "shows": shows, "ep": ep}
        return render(request, "editepisode.html", ctx)
