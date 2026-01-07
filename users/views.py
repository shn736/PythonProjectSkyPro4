import secrets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserManagersForm, UserRegisterForm
from users.models import User


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class UserDetailView(DetailView):
    model = User
    template_name = "../templates/MailingListManagement/user_detail.html"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "user_form.html"
    success_url = reverse_lazy("mailing_list_management:home")

    def get_form_class(self):
        user = self.request.user
        if user.has_perm("catalog.can_unpublish_product"):
            return UserManagersForm
        raise PermissionDenied


class UserListView(ListView):
    model = User
    template_name = "user_list.html"

    def get_queryset(self):
        if self.request.user.has_perm("can_view_mailing"):
            return User.objects.all()
        raise PermissionDenied
