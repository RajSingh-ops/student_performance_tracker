from django.utils import timezone
from .models import DailyEntry, DailyScore, Criterion

def notifications_processor(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user
    today = timezone.localtime().date()

    # 1. Check if entry exists
    has_entry_today = DailyEntry.objects.filter(user=user, date=today).exists()
    
    # 2. Check if AI analysis exists (only if entry exists)
    has_analysis = False
    if has_entry_today:
        entry = DailyEntry.objects.filter(user=user, date=today).first()
        has_analysis = DailyScore.objects.filter(entry=entry).exists()

    # 3. Check if goals (criteria) exist
    has_goals = Criterion.objects.filter(user=user).exists()

    return {
        'state_has_entry': has_entry_today,
        'state_has_analysis': has_analysis,
        'state_has_goals': has_goals,
    }