# urls.py — Маршрутизатор URL приложения accounts для системы управления складом (WMS)
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, reverse_lazy
from . import views

app_name = "accounts"

urlpatterns = [
    
    # Администрирование
    path('admin/', admin.site.urls),
    
    # Аутентификация и регистрация
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('register/', views.register_view, name='register'),
    path('signup/', views.signup, name='signup'),  # Имя маршрута 'signup'

    # Профиль сотрудника
    path("profile/", views.profile_view, name="profile"),
    path("update/", views.UserUpdateView.as_view(), name="my_account"),

    # Смена и сброс пароля
    path("password-change/", auth_views.PasswordChangeView.as_view(template_name="accounts/password_change.html", success_url=reverse_lazy("accounts:password_change_done")), name="password_change"),
    path("password-change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"), name="password_change_done"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html", email_template_name="accounts/email/password_reset_email.html", subject_template_name="accounts/email/password_reset_subject.txt", success_url=reverse_lazy("accounts:password_reset_done")), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html", success_url=reverse_lazy("accounts:password_reset_complete")), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),

    # Панель менеджера / админа: Управление кладовщиками
    path("manage/storekeepers/", views.StorekeeperListView.as_view(), name="storekeeper_list"),
    path("manage/storekeepers/add/", views.StorekeeperCreateView.as_view(), name="storekeeper_create"),
    path("manage/storekeepers/<int:pk>/edit/", views.StorekeeperUpdateView.as_view(), name="storekeeper_update"),
    path("manage/storekeepers/<int:pk>/delete/", views.StorekeeperDeleteView.as_view(), name="storekeeper_delete"),
]