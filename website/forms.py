from django import forms
from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions

from .models import DJ, Episode, Show


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
        )

    def clean_username(self):
        data = self.cleaned_data.get("username")
        if any(c in """ !@#$%^&*()"'-+?_=,<>/""" for c in data):
            raise forms.ValidationError("contains special characters")
        if len(data) <= 2:
            raise forms.ValidationError("username too short")
        return data

    def clean_password(self):
        data = self.cleaned_data.get("password")
        if len(data) <= 5:
            raise forms.ValidationError("password too short")
        return data


class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)

    def clean_username(self):
        data = self.cleaned_data.get("username")
        if User.objects.filter(username=data).exists():
            raise forms.ValidationError("username already in use")
        if any(c in """ !@#$%^&*()"'-+?_=,<>/""" for c in data):
            raise forms.ValidationError("contains special characters")
        if len(data) <= 2:
            raise forms.ValidationError("username too short")
        return data


class PasswordChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("password",)

    def clean_password(self):
        data = self.cleaned_data.get("password")
        if len(data) <= 5:
            raise forms.ValidationError("password too short")
        return data


class CustomizationForm(forms.ModelForm):
    class Meta:
        model = DJ
        fields = (
            "profile_pic",
            "bio",
            "profile_theme",
        )

    def clean_profile_pic(self):
        pfp = self.cleaned_data.get("profile_pic")
        if pfp:
            w, h = get_image_dimensions(pfp)
            if w > 200 or h > 200:
                raise forms.ValidationError("profile picture larger than 200x200")
            return pfp


class CreateShowForm(forms.ModelForm):
    description = forms.CharField(required=False)

    class Meta:
        model = Show
        fields = ("banner", "name", "description")


class CreateEpisodeForm(forms.ModelForm):
    description = forms.CharField(required=False)

    class Meta:
        model = Episode
        fields = ("name", "description", "link", "show")

    def clean_show(self):
        show = self.cleaned_data.get("show")

        try:
            print(show.name)
        except Show.DoesNotExist:
            raise forms.ValidationError("show does not exist") from None
        except ValueError:
            raise forms.ValidationError("unknown value passed") from None

        if show == -1:
            raise forms.ValidationError("show not selected")

        return show

    def clean_link(self):
        data = self.cleaned_data.get("link")

        if "https://soundcloud.com/" not in data:
            raise forms.ValidationError("only links from soundcloud are allowed")

        if "/sets" in data:
            raise forms.ValidationError("sets are not allowed, only single songs (no time limit)")

        return data
