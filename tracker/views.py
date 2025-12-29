from collections import defaultdict
import random
import json
from .models import Achievement
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Achievement, AchievementLike, AchievementComment

from .models import Criterion, DailyEntry, DailyScore, Profile, Review


def handler404(request, exception=None):
    """Redirect 404 errors to dashboard."""
    return redirect('dashboard')


@login_required
def dashboard_view(request):
    user = request.user

    entries = DailyEntry.objects.filter(user=user).order_by("date")

    # Daily performance line chart
    line_labels = []
    line_values = []

    for e in entries:
        line_labels.append(e.date.isoformat())
        # compute per-day average across criteria
        values = [int(v) for v in e.ratings.values()] if e.ratings else [0]
        total = sum(values)
        count = len(values) if len(values) > 0 else 1
        avg = round(total / count, 2)
        line_values.append(avg)

    # Monthly average bar chart
    month_data = defaultdict(list)

    for e in entries:
        month = e.date.strftime("%b")
        values = [int(v) for v in e.ratings.values()] if e.ratings else [0]
        total = sum(values)
        count = len(values) if len(values) > 0 else 1
        avg = round(total / count, 2)
        month_data[month].append(avg)

    month_labels = list(month_data.keys())
    month_scores = [round(sum(v) / len(v), 2) for v in month_data.values()]

    # Heatmap score normalization
    daily_scores = [
        {
            "date": e.date.isoformat(),
            "score": round(sum([int(v) for v in e.ratings.values()]) / (len(e.ratings) if len(e.ratings) > 0 else 1), 2)
        }
        for e in entries
    ]

    # prepare JSON-serializable data for template JS
    score_data = {d["date"]: d["score"] for d in daily_scores}

    # pie chart counts (5 categories) based on per-criterion average (1..5)
    excellent = sum(1 for d in daily_scores if d["score"] >= 4.5)
    very_good = sum(1 for d in daily_scores if 3.5 <= d["score"] < 4.5)
    average = sum(1 for d in daily_scores if 2.5 <= d["score"] < 3.5)
    below_avg = sum(1 for d in daily_scores if 1.5 <= d["score"] < 2.5)
    poor = sum(1 for d in daily_scores if d["score"] < 1.5)

    return render(request, "dashboard.html", {
        "line_labels": json.dumps(line_labels),
        "line_values": json.dumps(line_values),
        "month_labels": json.dumps(month_labels),
        "month_scores": json.dumps(month_scores),
        "score_data": json.dumps(score_data),
        "join_date": user.date_joined.date().isoformat(),
        "today": timezone.localdate().isoformat(),
        "excellent": excellent,
        "very_good": very_good,
        "average": average,
        "below_avg": below_avg,
        "poor": poor,
    })


@login_required
def criteria_setup_view(request):
    user = request.user

    if request.method == "POST":
        Criterion.objects.filter(user=user).delete()

        names = [
            request.POST.get("crit1"),
            request.POST.get("crit2"),
            request.POST.get("crit3"),
            request.POST.get("crit4"),
            request.POST.get("crit5"),
        ]

        order = 0
        for name in names:
            if name and name.strip():
                Criterion.objects.create(user=user, name=name.strip(), order=order)
                order += 1

        return redirect("daily-entry")

    return render(request, "criteria_setup.html")


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect("password-reset")

        otp = random.randint(100000, 999999)
        request.session["reset_email"] = email
        request.session["reset_otp"] = otp

        send_mail(
            "Your OTP for Password Reset",
            f"Your OTP code is: {otp}",
            "your_email@gmail.com",
            [email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent to your email.")
        return redirect("password-reset-verify")

    return render(request, "registration/password_reset_email.html")


def password_reset_verify(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("password-reset-verify")

        saved_email = request.session.get("reset_email")
        saved_otp = str(request.session.get("reset_otp"))

        if otp != saved_otp:
            messages.error(request, "Invalid OTP.")
            return redirect("password-reset-verify")

        try:
            user = User.objects.get(email=saved_email)
        except User.DoesNotExist:
            messages.error(request, "Account not found.")
            return redirect("password-reset")

        user.set_password(password1)
        user.save()

        request.session.pop("reset_email", None)
        request.session.pop("reset_otp", None)

        messages.success(request, "Password reset successful. Login now.")
        return redirect("login")

    return render(request, "registration/password_reset_verify.html")


@login_required
def about_me_view(request):
    return render(request, "about_me.html")


@login_required
def review_panel(request):
    user = request.user

    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        message = request.POST.get("message", "").strip()

        if message:
            Review.objects.create(user=user, rating=rating, message=message)
            messages.success(request, "Thank you for your review!")
            return redirect("review")

    reviews = Review.objects.all().order_by("-created_at")

    if reviews.exists():
        avg = sum(r.rating for r in reviews) / reviews.count()
        avg = round(avg, 2)
    else:
        avg = 0

    return render(request, "review_panel.html", {"reviews": reviews, "avg_rating": avg, "avg_full": int(avg)})


class MyLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("dashboard")

    def get_success_url(self):
        return self.success_url


@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, "profile.html", {"profile": profile})


@login_required
def edit_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        profile.bio = request.POST.get("bio")
        profile.instagram = request.POST.get("instagram")
        profile.twitter = request.POST.get("twitter")
        profile.linkedin = request.POST.get("linkedin")
        profile.github = request.POST.get("github")

        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        if "header_image" in request.FILES:
            profile.header_image = request.FILES["header_image"]

        profile.save()
        messages.success(request, "Profile Updated Successfully!")
        return redirect("profile")

    return render(request, "edit_profile.html", {"profile": profile})


@login_required
def daily_entry_view(request):
    user = request.user
    today = timezone.localdate()

    criterias = Criterion.objects.filter(user=user).order_by("order")
    if not criterias.exists():
        return redirect("criteria")

    entry = DailyEntry.objects.filter(user=user, date=today).first()

    if request.method == "POST":
        ratings = {}

        for c in criterias:
            rating = int(request.POST.get(f"rating_{c.id}", 1))
            rating = max(1, min(5, rating))
            ratings[c.name] = rating

        reflection = request.POST.get("reflection", "").strip()

        DailyEntry.objects.update_or_create(
            user=user,
            date=today,
            defaults={
                "ratings": ratings,
                "reflection": reflection,
            },
        )

        messages.success(request, "Your daily entry is saved!")
        return redirect("daily")

    return render(request, "daily_entry.html", {
        "criteria": criterias,
        "existing_ratings": entry.ratings if entry else {},
        "entry": entry,
        "today": today,
    })




@login_required
def social_view(request):
    users = User.objects.all().order_by("username")
    return render(request, "social.html", {"users": users})


@login_required
def daily_view(request):
    user = request.user
    today = timezone.localdate()

    try:
        entry = DailyEntry.objects.get(user=user, date=today)
    except DailyEntry.DoesNotExist:
        return redirect("daily-entry")

    return render(request, "daily.html", {"entry": entry})


def privacy_policy(request):
    return render(request, "privacy_policy.html")

def terms_conditions(request):
    return render(request, "terms.html")
@login_required
def create_achievement(request):
    if request.method == "POST":
        Achievement.objects.create(
            user=request.user,
            title=request.POST.get("title"),
            description=request.POST.get("description", ""),
            image=request.FILES.get("image")
        )
        return redirect("achievements")

    # If someone opens /create/ directly
    return redirect("achievements")

@login_required
def achievements_page(request):
    achievements = Achievement.objects.all().order_by("-created_at")
    return render(request, "achievements.html", {
        "achievements": achievements
    })
@login_required
@require_POST
def toggle_like(request, id):
    achievement = get_object_or_404(Achievement, id=id)

    like, created = AchievementLike.objects.get_or_create(
        user=request.user,
        achievement=achievement
    )

    if not created:
        like.delete()

    return JsonResponse({
        "likes": AchievementLike.objects.filter(
            achievement=achievement
        ).count()
    })
@login_required
@require_POST
def add_comment(request, id):
    AchievementComment.objects.create(
        user=request.user,
        achievement_id=id,
        text=request.POST.get("comment")
    )
    return redirect("achievements")
def landing_page(request):
    return render(request, "landing.html")

def about_page(request):
    return render(request, "about.html")
from django.views.decorators.http import require_POST
from django.conf import settings
import google.generativeai as genai

@require_POST
@login_required
def analyze_entry(request):
    user = request.user
    today = timezone.localdate()

    entry = get_object_or_404(DailyEntry, user=user, date=today)

    # Prepare text for Gemini
    ratings_text = "\n".join(
        [f"{k}: {v}/5" for k, v in entry.ratings.items()]
    )

    reflection = entry.reflection or "No reflection provided."

    prompt = f"""
You are a self-improvement coach.

Ratings:
{ratings_text}

User reflection:
{reflection}

Give:
1. A short score out of 100
2. A brief explanation (max 5 lines)
"""

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")

    response = model.generate_content(prompt)
    output = response.text.strip()

    # Very simple score extraction
    score = 0
    for word in output.split():
        if word.isdigit():
            score = min(int(word), 100)
            break

    DailyScore.objects.update_or_create(
        entry=entry,
        defaults={
            "score": score,
            "explanation": output
        }
    )

    messages.success(request, "Analysis complete!")
    return redirect("daily")
