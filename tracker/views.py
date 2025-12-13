from collections import defaultdict
import random
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone

from .models import Criterion, DailyEntry, DailyScore, Profile, Review


@login_required
def dashboard_view(request):
    user = request.user

    entries = DailyEntry.objects.filter(user=user).order_by("date")

    # Daily performance line chart
    line_labels = []
    line_values = []

    for e in entries:
        line_labels.append(e.date.isoformat())
        # ensure values are numeric
        total = sum(int(v) for v in e.ratings.values())
        line_values.append(total)

    # Monthly average bar chart
    month_data = defaultdict(list)

    for e in entries:
        month = e.date.strftime("%b")
        total = sum(int(v) for v in e.ratings.values())
        month_data[month].append(total)

    month_labels = list(month_data.keys())
    month_scores = [sum(v) / len(v) for v in month_data.values()]

    # Heatmap score normalization
    daily_scores = [
        {"date": e.date.isoformat(), "score": sum(int(v) for v in e.ratings.values())}
        for e in entries
    ]

    # prepare JSON-serializable data for template JS
    score_data = {d["date"]: d["score"] for d in daily_scores}

    # pie chart counts (buckets aligned with heatmap colors)
    excellent = sum(1 for d in daily_scores if d["score"] >= 120)
    great = sum(1 for d in daily_scores if 100 <= d["score"] < 120)
    average = sum(1 for d in daily_scores if 50 <= d["score"] < 100)
    poor = sum(1 for d in daily_scores if d["score"] < 50)

    return render(request, "dashboard.html", {
        "line_labels": json.dumps(line_labels),
        "line_values": json.dumps(line_values),
        "month_labels": json.dumps(month_labels),
        "month_scores": json.dumps(month_scores),
        "score_data": json.dumps(score_data),
        "join_date": user.date_joined.date().isoformat(),
        "today": timezone.localdate().isoformat(),
        "excellent": excellent,
        "good": great,
        "average": average,
        "bad": poor,
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

    try:
        entry = DailyEntry.objects.get(user=user, date=today)
    except DailyEntry.DoesNotExist:
        entry = None

    if request.method == "POST":
        ratings = {}
        descriptions = {}

        for c in criterias:
            rating = int(request.POST.get(f"rating_{c.id}", 0))
            desc = request.POST.get(f"desc_{c.id}", "")
            ratings[c.name] = rating
            descriptions[c.name] = desc

        DailyEntry.objects.update_or_create(
            user=user,
            date=today,
            defaults={"ratings": ratings, "descriptions": descriptions},
        )

        messages.success(request, "Your daily entry is saved!")
        return redirect("dashboard")

    return render(request, "daily_entry.html", {"criterias": criterias, "entry": entry, "today": today})
