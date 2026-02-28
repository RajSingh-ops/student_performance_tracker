from collections import defaultdict
import random
import json
import google.generativeai as genai
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import DailyEntry, DailyScore, Profile, Review, Quiz, QuizResult


def handler404(request, exception=None):
    """Redirect 404 errors to dashboard."""
    return redirect('dashboard')
from .models import DailyEntry

@login_required
def dashboard_view(request):
    user = request.user
    current_year = 2026 
    entries = DailyEntry.objects.filter(
        user=user, 
        date__year=current_year
    ).order_by("date")

    line_labels = []
    line_values = []
    month_data = defaultdict(list)
    score_data = {}

    excellent = 0
    very_good = 0
    average = 0
    below_avg = 0
    poor = 0

    for e in entries:
        date_str = e.date.isoformat()
        
        quiz_results = QuizResult.objects.filter(quiz__entry=e, passed=True)
        
        if quiz_results.exists():
            daily_score = sum(r.score for r in quiz_results) / quiz_results.count()
            daily_score = round(daily_score / 20, 2)  # Convert to 1-5 scale
        else:
            daily_score = 0

        line_labels.append(date_str)
        line_values.append(daily_score)

        month_name = e.date.strftime("%b")
        month_data[month_name].append(daily_score)

        score_data[date_str] = daily_score

        if daily_score >= 4.5: excellent += 1
        elif daily_score >= 3.5: very_good += 1
        elif daily_score >= 2.5: average += 1
        elif daily_score >= 1.5: below_avg += 1
        elif daily_score > 0: poor += 1

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

    entry = DailyEntry.objects.filter(user=user, date=today).first()

    if request.method == "POST":
        subjects = {
            'dsa': request.POST.get('dsa_description', '').strip(),
            'os': request.POST.get('os_description', '').strip(),
            'dbms': request.POST.get('dbms_description', '').strip(),
            'cn': request.POST.get('cn_description', '').strip(),
            'system_design': request.POST.get('system_design_description', '').strip(),
        }

        reflection = request.POST.get("reflection", "").strip()

        DailyEntry.objects.update_or_create(
            user=user,
            date=today,
            defaults={
                'dsa_description': subjects['dsa'],
                'os_description': subjects['os'],
                'dbms_description': subjects['dbms'],
                'cn_description': subjects['cn'],
                'system_design_description': subjects['system_design'],
                'reflection': reflection,
            },
        )

        messages.success(request, "Your daily entry is saved!")
        return redirect("daily")

    return render(request, "daily_entry.html", {
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

    quiz_results = QuizResult.objects.filter(quiz__entry=entry).order_by('-created_at')

    return render(request, "daily.html", {
        "entry": entry,
        "quiz_results": quiz_results,
    })


def generate_sample_subject_quiz(subject, topic):
    """Generate 4 sample quiz questions for a specific subject"""
    questions = []
    
    for i in range(1, 5):
        questions.append({
            "question": f"Question {i} about {subject.upper()}?",
            "options": {"A": f"Option A{i}", "B": f"Option B{i}", "C": f"Option C{i}", "D": f"Option D{i}"},
            "correct": ["A", "B", "C", "D"][i % 4],
            "subject": subject
        })
    
    return questions


@login_required
def start_quiz(request):
    """Start a unified quiz: 20 questions from all 5 subjects"""
    user = request.user
    today = timezone.localdate()

    entry = get_object_or_404(DailyEntry, user=user, date=today)

    topics_data = {
        'DSA': entry.dsa_description or 'Data Structures and Algorithms',
        'OS': entry.os_description or 'Operating Systems',
        'DBMS': entry.dbms_description or 'Database Management',
        'CN': entry.cn_description or 'Computer Networks',
        'SYSTEM_DESIGN': entry.system_design_description or 'System Design',
    }

    all_questions = []
    
    for subject, topic in topics_data.items():
        try:
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel("models/gemini-2.5-flash")

                prompt = f"""Generate exactly 4 multiple-choice questions as JSON only.
Topic: {topic}
Subject: {subject}

Return ONLY valid JSON array, no other text:
[
  {{"question": "Question text?", "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}}, "correct": "A"}},
]
Make exactly 4 questions that test understanding of {topic}. Each option should be plausible."""

                import json
                
                try:
                    response = model.generate_content(prompt)
                    response_text = response.text.strip()

                    start_idx = response_text.find('[')
                    end_idx = response_text.rfind(']') + 1
                    
                    if start_idx != -1 and end_idx > start_idx:
                        try:
                            json_str = response_text[start_idx:end_idx]
                            subject_questions = json.loads(json_str)
                            if len(subject_questions) >= 4:
                                for q in subject_questions[:4]:
                                    q['subject'] = subject
                                all_questions.extend(subject_questions[:4])
                            else:
                                fallback_qs = generate_sample_subject_quiz(subject, topic)
                                all_questions.extend(fallback_qs)
                        except:
                            fallback_qs = generate_sample_subject_quiz(subject, topic)
                            all_questions.extend(fallback_qs)
                    else:
                        fallback_qs = generate_sample_subject_quiz(subject, topic)
                        all_questions.extend(fallback_qs)
                except:
                    fallback_qs = generate_sample_subject_quiz(subject, topic)
                    all_questions.extend(fallback_qs)
        except:
            fallback_qs = generate_sample_subject_quiz(subject, topic)
            all_questions.extend(fallback_qs)

    if not all_questions:
        for subject, topic in topics_data.items():
            fallback_qs = generate_sample_subject_quiz(subject, topic)
            all_questions.extend(fallback_qs)

    try:
        quiz = Quiz.objects.create(
            user=user,
            entry=entry,
            subject='MIXED',  # Unified quiz label
            topic=', '.join(topics_data.values()),
            questions=all_questions[:20]
        )
        return redirect('take-quiz', quiz_id=quiz.id)
    except Exception as db_err:
        messages.error(request, f"Error creating quiz: {str(db_err)[:80]}")
        return redirect('daily')


def generate_sample_quiz(subject, topic):
    """Generate sample quiz questions as fallback"""
    questions = [
        {
            "question": f"Question 1 about {subject.upper()}?",
            "options": {"A": "Answer A", "B": "Answer B", "C": "Answer C", "D": "Answer D"},
            "correct": "A"
        },
    ]
    
    for i in range(2, 21):
        questions.append({
            "question": f"Question {i} about {topic}?",
            "options": {"A": f"Option A{i}", "B": f"Option B{i}", "C": f"Option C{i}", "D": f"Option D{i}"},
            "correct": ["A", "B", "C", "D"][i % 4]
        })
    
    return questions


@login_required
def take_quiz(request, quiz_id):
    """Display quiz questions for user to answer"""
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)

    return render(request, 'quiz.html', {
        'quiz': quiz,
        'questions': quiz.questions,
    })


@login_required
@require_POST
def submit_quiz(request, quiz_id):
    """Submit quiz answers and calculate score"""
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)

    answers = {}
    correct_count = 0

    for idx, question in enumerate(quiz.questions):
        answer_key = f'answer_{idx}'
        user_answer = request.POST.get(answer_key, '')
        answers[str(idx)] = user_answer

        if user_answer == question.get('correct'):
            correct_count += 1

    total_questions = len(quiz.questions)
    score = (correct_count / total_questions * 100) if total_questions > 0 else 0
    passed = score >= 60

    quiz_result = QuizResult.objects.create(
        user=request.user,
        quiz=quiz,
        answers=answers,
        score=score,
        passed=passed
    )

    update_daily_score_from_quizzes(quiz.entry)

    messages.success(request, f"Quiz submitted! Your score: {score:.1f}%")
    return redirect('daily')


def update_daily_score_from_quizzes(entry):
    """Update daily score based on quiz results"""
    quiz_results = QuizResult.objects.filter(quiz__entry=entry)

    if quiz_results.exists():
        avg_score = sum(r.score for r in quiz_results) / quiz_results.count()
        DailyScore.objects.update_or_create(
            entry=entry,
            defaults={
                'score': avg_score,
                'explanation': '',
            }
        )
    else:
        DailyScore.objects.filter(entry=entry).delete()


def privacy_policy(request):
    return render(request, "privacy_policy.html")

def terms_conditions(request):
    return render(request, "terms.html")

def landing_page(request):
    return render(request, "landing.html")

def about_page(request):
    return render(request, "about.html")
from django.views.decorators.http import require_POST
from django.conf import settings
import google.generativeai as genai

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
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

def view_other_profile(request, username):
    other_user = get_object_or_404(User, username=username)
    
    if request.user.is_authenticated and request.user == other_user:
        return redirect('profile') # 'profile' is your private view name
    
    return render(request, 'other_profile_template.html', {
        'other_user': other_user
    })
