from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import UserCreateView, UserListView, UserUpdateView, email_verification

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user_update"),
    path("email-confirm/<str:token>", email_verification, name="email-confirm"),
]
