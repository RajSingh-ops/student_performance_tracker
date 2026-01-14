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


import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from collections import defaultdict
from .models import DailyEntry

@login_required
def dashboard_view(request):
    user = request.user
    # 1. Filter entries specifically for the year 2026
    current_year = 2026 
    entries = DailyEntry.objects.filter(
        user=user, 
        date__year=current_year
    ).order_by("date")

    line_labels = []
    line_values = []
    month_data = defaultdict(list)
    score_data = {}

    # Performance categories for Pie Chart
    excellent = 0
    very_good = 0
    average = 0
    below_avg = 0
    poor = 0

    for e in entries:
        date_str = e.date.isoformat()
        
        # Calculate daily average across all criteria
        ratings = e.ratings.values() if e.ratings else [0]
        values = [int(v) for v in ratings]
        daily_avg = round(sum(values) / len(values), 2) if values else 0

        # Prepare Line Chart data
        line_labels.append(date_str)
        line_values.append(daily_avg)

        # Prepare Monthly Bar Chart data
        month_name = e.date.strftime("%b")
        month_data[month_name].append(daily_avg)

        # Prepare Heatmap data
        score_data[date_str] = daily_avg

        # Categorize for Pie Chart
        if daily_avg >= 4.5: excellent += 1
        elif daily_avg >= 3.5: very_good += 1
        elif daily_avg >= 2.5: average += 1
        elif daily_avg >= 1.5: below_avg += 1
        else: poor += 1

    # Format Monthly Averages
    # We use a list of month names to keep them in order Jan-Dec
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    final_month_labels = []
    final_month_scores = []

    for m in month_order:
        if m in month_data:
            final_month_labels.append(m)
            avg_score = round(sum(month_data[m]) / len(month_data[m]), 2)
            final_month_scores.append(avg_score)

    context = {
        "line_labels": json.dumps(line_labels),
        "line_values": json.dumps(line_values),
        "month_labels": json.dumps(final_month_labels),
        "month_scores": json.dumps(final_month_scores),
        "score_data": json.dumps(score_data),
        "join_date": user.date_joined.date().isoformat(),
        "today": timezone.localdate().isoformat(),
        "excellent": excellent,
        "very_good": very_good,
        "average": average,
        "below_avg": below_avg,
        "poor": poor,
    }

    return render(request, "dashboard.html", context)


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


from django.conf import settings

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

        try:
            send_mail(
                "Your OTP for Password Reset",
                f"Your OTP code is: {otp}",
                settings.DEFAULT_FROM_EMAIL,  # ✅ FIX
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print("Password reset email error:", e)
            messages.error(request, "Email service temporarily unavailable.")
            return redirect("password-reset")

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

    # Prepare ratings text
    ratings_text = "\n".join(
        f"{k}: {v}/5" for k, v in entry.ratings.items()
    )

    reflection = entry.reflection or "No reflection provided."

    prompt = f"""
Here is the user's daily performance.

Ratings:
{ratings_text}

Overall reflection:
{reflection}

Task:
Give short advice and motivation in about 10000 characters.
Be positive, practical, and encouraging.
"""

    genai.configure(api_key=settings.GEMINI_API_KEY)

    # ✅ Correct placement
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    output = response.text.strip()

    # ✅ Calculate score from ratings (NOT from AI text)
    avg_rating = sum(entry.ratings.values()) / len(entry.ratings)
    score = int((avg_rating / 5) * 100)

    DailyScore.objects.update_or_create(
        entry=entry,
        defaults={
            "score": score,
            "explanation": output
        }
    )

    messages.success(request, "Analysis complete!")
    return redirect("daily")
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def delete_account_view(request):
    if request.method == "POST":
        user = request.user
        logout(request)        # logout first
        user.delete()          # deletes user + cascades profile
        return redirect("landing")

    return render(request, "delete_account.html")
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

def view_other_profile(request, username):
    # 1. Find the user being requested
    other_user = get_object_or_404(User, username=username)
    
    # 2. THE SELF CASE:
    # If the logged-in user clicks on themselves, redirect them to their own dashboard
    if request.user.is_authenticated and request.user == other_user:
        return redirect('profile') # 'profile' is your private view name
    
    # 3. Otherwise, show them the public template
    return render(request, 'other_profile_template.html', {
        'other_user': other_user
    })
from .models import Help
@login_required
def help(request):
    help=Help.objects.all().order_by("-created_at")
    return render(request,"help.html",{"help":help})