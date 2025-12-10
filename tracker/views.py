from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DailyEntry, Criterion, DailyScore,Review
from django.contrib.auth.decorators import login_required
from django.utils import timezone



@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.localdate()

    # fetch all daily scores
    daily_scores = DailyScore.objects.filter(entry__user=user).order_by("entry__date")

    # --- Heatmap data ---
    score_data = {
        ds.entry.date.isoformat(): ds.score
        for ds in daily_scores
    }

    # --- Line Chart (Daily score trend) ---
    line_labels = [ds.entry.date.isoformat() for ds in daily_scores]
    line_values = [ds.score for ds in daily_scores]

    # --- Monthly Average Chart ---
    from collections import defaultdict
    month_scores_map = defaultdict(list)

    for ds in daily_scores:
        month = ds.entry.date.strftime("%Y-%m")
        month_scores_map[month].append(ds.score)

    month_labels = list(month_scores_map.keys())
    month_scores = [sum(v)/len(v) for v in month_scores_map.values()]

    # --- Pie Chart (Performance distribution) ---
    excellent = sum(1 for ds in daily_scores if ds.score >= 120)
    good = sum(1 for ds in daily_scores if 110 <= ds.score < 120)
    average = sum(1 for ds in daily_scores if 80 <= ds.score < 110)
    bad = sum(1 for ds in daily_scores if ds.score < 80)

    return render(request, "dashboard.html", {
        "today": today.isoformat(),
        "join_date": user.date_joined.date().isoformat(),
        "score_data": score_data,

        # chart data
        "line_labels": line_labels,
        "line_values": line_values,

        "month_labels": month_labels,
        "month_scores": month_scores,

        "excellent": excellent,
        "good": good,
        "average": average,
        "bad": bad,
    })




@login_required
def daily_entry_view(request):
    user = request.user
    today = timezone.localdate()

    # Fetch user criteria
    criteria = Criterion.objects.filter(user=user)
    if not criteria.exists():
        return redirect("criteria")   # User must create criteria first

    # Try to load existing entry (for pre-fill)
    try:
        entry = DailyEntry.objects.get(user=user, date=today)
    except DailyEntry.DoesNotExist:
        entry = None

    # Prepare dictionaries for template pre-fill
    existing_ratings = entry.ratings if entry else {}
    existing_descriptions = entry.descriptions if entry else {}

    # ---------------------------
    # HANDLE FORM SUBMISSION
    # ---------------------------
    if request.method == "POST":
        ratings = {}
        descriptions = {}

        for c in criteria:
            rating = int(request.POST.get(f"rating_{c.id}", 0))
            desc = request.POST.get(f"desc_{c.id}", "").strip()

            # Validate word limit
            if len(desc.split()) > 30:
                messages.error(request, f"Description for {c.name} exceeds 30 words.")
                return redirect("daily-entry")

            # Use criterion.name as dictionary key
            ratings[c.name] = rating
            descriptions[c.name] = desc

        # Save or update the entry
        DailyEntry.objects.update_or_create(
            user=user,
            date=today,
            defaults={"ratings": ratings, "descriptions": descriptions},
        )

        messages.success(request, "Your daily entry is saved!")
        return redirect("dashboard")

    # ---------------------------
    # RENDER TEMPLATE
    # ---------------------------
    return render(
        request,
        "daily_entry.html",
        {
            "criteria": criteria,
            "today": today,
            "existing_ratings": existing_ratings,
            "existing_descriptions": existing_descriptions,
        },
    )
from .models import Criterion


@login_required
def criteria_setup_view(request):
    user = request.user

    if request.method == "POST":
        # delete old criteria
        Criterion.objects.filter(user=user).delete()

        # read 5 inputs
        names = [
            request.POST.get("crit1"),
            request.POST.get("crit2"),
            request.POST.get("crit3"),
            request.POST.get("crit4"),
            request.POST.get("crit5"),
        ]

        # create criteria with unique order index
        order = 0
        for name in names:
            if name and name.strip():
                Criterion.objects.create(
                    user=user,
                    name=name.strip(),
                    order=order
                )
                order += 1

        return redirect("daily-entry")

    return render(request, "criteria_setup.html")
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
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

        user = User.objects.get(email=saved_email)
        user.set_password(password1)
        user.save()

        # Clear session
        del request.session["reset_email"]
        del request.session["reset_otp"]

        messages.success(request, "Password reset successful. Login now.")
        return redirect("login")

    return render(request, "registration/password_reset_verify.html")
@login_required
def about_me_view(request):
    return render(request, "about_me.html")
@login_required
def review_panel(request):
    user = request.user

    # Handle POST review submission
    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        message = request.POST.get("message", "").strip()

        if message:
            Review.objects.create(user=user, rating=rating, message=message)
            messages.success(request, "Thank you for your review!")
            return redirect("review")

    # Fetch all reviews
    reviews = Review.objects.all().order_by("-created_at")

    # Compute average rating
    if reviews.exists():
        avg = sum(r.rating for r in reviews) / reviews.count()
        avg = round(avg, 2)
    else:
        avg = 0

    return render(
        request,
        "review_panel.html",
        {
            "reviews": reviews,
            "avg_rating": avg,
            "avg_full": int(avg),
        }
    )
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView

class MyLoginView(LoginView):
    template_name = "registration/login.html"   # your login template
    redirect_authenticated_user = True          # built-in redirect (Django 2.1+)

    # optional: if you want to force redirect target
    def get_success_url(self):
        return redirect("dashboard").url
# tracker/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, "profile.html", {"profile": profile})


@login_required
def edit_profile_view(request):
    profile = Profile.objects.get(user=request.user)

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
