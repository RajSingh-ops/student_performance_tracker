from django.utils import timezone
from .models import DailyEntry, DailyScore, Criterion

def notifications_processor(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user
    today = timezone.localtime().date()

    # Data check
    has_entry = DailyEntry.objects.filter(user=user, date=today).exists()
    has_analysis = False
    if has_entry:
        entry = DailyEntry.objects.filter(user=user, date=today).first()
        has_analysis = DailyScore.objects.filter(entry=entry).exists()
    has_goals = Criterion.objects.filter(user=user).exists()

    return {
        'show_entry_msg': not has_entry,
        'show_analysis_msg': has_entry and not has_analysis,
        'show_goal_msg': not has_goals,
    }