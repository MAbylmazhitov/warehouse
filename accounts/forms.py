# forms.py — Определение и настройка форм для валидации, обработки и стилизации вводимых пользователем данных.
# В методах __init__ автоматически проставляются CSS-классы Bootstrap (form-control) для корректного отображения интерфейса.
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Profile
from django.contrib.auth.models import User

User = get_user_model()


# Расширяет стандартную форму регистрации, добавляя поля имени, фамилии, телефона и электронной почты,
# проверяет уникальность email и автоматически сохраняет введенный номер телефона в связанную модель Profile.
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label=_("First name"), max_length=100, required=True, widget=forms.TextInput(attrs={"placeholder": _("First name")}))
    last_name = forms.CharField(label=_("Last name"), max_length=100, required=False, widget=forms.TextInput(attrs={"placeholder": _("Last name")}))
    phone = forms.CharField(label=_("Phone Number"), max_length=20, required=True, widget=forms.TextInput(attrs={"placeholder": "+7 (700) 000-00-00"}))
    email = forms.EmailField(label=_("Email address"), required=False, widget=forms.EmailInput(attrs={"placeholder": "example@mail.com"}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "phone", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = f'{field.widget.attrs.get("class", "")} form-control form-control-lg rounded-3'.strip()

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with this email address already exists."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data.get("email", "")

        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone")
            profile.save()

        return user


            
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First Name"), required=False)
    last_name = forms.CharField(label=_("Last Name"), required=False)
    email = forms.EmailField(label=_("Email Address"), required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class WarehouseProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "employee_code", "avatar"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != "avatar":
                field.widget.attrs.update({"class": "form-control"})
            else:
                field.widget.attrs.update({"class": "form-control-file"})            