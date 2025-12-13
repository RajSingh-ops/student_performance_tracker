from django.urls import path
from .views import dashboard_view
from .views_auth import register_view
from .views import daily_entry_view,criteria_setup_view,password_reset_request,password_reset_verify
from . import views
urlpatterns = [
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('daily-entry/', daily_entry_view, name='daily-entry'),
    path('criteria/', criteria_setup_view, name='criteria'),
    path("password-reset/", password_reset_request, name="password-reset"),
    path("password-reset/verify/", password_reset_verify, name="password-reset-verify"),
    path("about-me/", views.about_me_view, name="about-me"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit-profile"),
    path("social/", views.social_view, name="social"),
    path("daily/", views.daily_view, name="daily"),
]
