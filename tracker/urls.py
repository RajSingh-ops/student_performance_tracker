from django.urls import path
from .views import dashboard_view
from .views_auth import register_view
from .views import daily_entry_view,criteria_setup_view,password_reset_request,password_reset_verify
from . import views
from .views import (
    achievements_page,
    toggle_like,
    add_comment,
    create_achievement,
    landing_page
)
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
    path("privacy-policy/", views.privacy_policy, name="privacy-policy"),
    path("terms/", views.terms_conditions, name="terms"),
    #Achievements feed page
    path("achievements/", achievements_page, name="achievements"),
    path("achievements/create/", create_achievement, name="create_achievement"),
    path("account/delete/", views.delete_account_view, name="delete-account"),
    path("help/", views.help_page, name="help"),
    path("help/create/", views.create_help, name="create_help"),
    path("help/<int:id>/like/", views.like_help, name="like_help"),
    path("help/<int:id>/comment/", views.add_help_comment, name="add_help_comment"),
    # Like / Unlike (AJAX)
    path("achievements/<int:id>/like/", toggle_like, name="toggle_like"),
    path("daily/analyze/", views.analyze_entry, name="analyze-entry"),

    # Add comment
    path("achievements/<int:id>/comment/", add_comment, name="add_comment"),
    path("/aboutwebsite", views.about_page, name="about website"),
    path("", landing_page, name="landing"),
    # urls.py
    path('viewprofile/<str:username>/', views.view_other_profile, name='view_other_profile'),
]
