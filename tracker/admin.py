from django.contrib import admin
from .models import DailyEntry, Quiz, QuizResult

admin.site.register(DailyEntry)
admin.site.register(Quiz)
admin.site.register(QuizResult)
