from django.urls import path
from .views import dashboard_view
from .views_auth import register_view
from .views import daily_entry_view,password_reset_request,password_reset_verify
from . import views
from .views import landing_page

urlpatterns = [
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('daily-entry/', daily_entry_view, name='daily-entry'),
    path("password-reset/", password_reset_request, name="password-reset"),
    path("password-reset/verify/", password_reset_verify, name="password-reset-verify"),
    path("about-me/", views.about_me_view, name="about-me"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit-profile"),
    path("social/", views.social_view, name="social"),
    path("daily/", views.daily_view, name="daily"),
    path("privacy-policy/", views.privacy_policy, name="privacy-policy"),
    path("terms/", views.terms_conditions, name="terms"),
    path("account/delete/", views.delete_account_view, name="delete-account"),
    path("daily/quiz/start/", views.start_quiz, name="start-quiz"),
    path("daily/quiz/<int:quiz_id>/", views.take_quiz, name="take-quiz"),
    path("daily/quiz/<int:quiz_id>/submit/", views.submit_quiz, name="submit-quiz"),
    path("/aboutwebsite", views.about_page, name="about website"),
    path("", landing_page, name="landing"),
    path('viewprofile/<str:username>/', views.view_other_profile, name='view_other_profile'),
]
