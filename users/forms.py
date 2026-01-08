from django.contrib.auth.forms import UserCreationForm
from django.forms import BooleanField, ModelForm

from users.models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control"


class UserManagersForm(StyleFormMixin, ModelForm):
    class Meta:
        model = User
        fields = ("is_active",)
