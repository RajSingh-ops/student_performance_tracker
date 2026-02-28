from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Criterion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="criteria")
    name = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=0)  # For sorting criteria

    class Meta:
        ordering = ["order"]
        unique_together = ("user", "order")

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class DailyEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entries")
    date = models.DateField()

    dsa_description = models.TextField(blank=True)
    os_description = models.TextField(blank=True)
    dbms_description = models.TextField(blank=True)
    cn_description = models.TextField(blank=True)
    system_design_description = models.TextField(blank=True)

    reflection = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]



class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quizzes")
    entry = models.ForeignKey(DailyEntry, on_delete=models.CASCADE, related_name="quizzes")
    subject = models.CharField(max_length=50)  # DSA, OS, DBMS, CN, System Design
    topic = models.CharField(max_length=200)  # What they did (from text input)
    questions = models.JSONField()  # List of 20 questions with options
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz: {self.user.username} - {self.subject}: {self.topic}"


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_results")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    answers = models.JSONField()  # User's selected answers
    score = models.FloatField()  # Percentage (0-100)
    passed = models.BooleanField()  # True if score >= 60
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.subject}: {self.score}%"


class DailyScore(models.Model):
    entry = models.OneToOneField(DailyEntry, on_delete=models.CASCADE, related_name="score")
    score = models.FloatField()  # Example: 113.0
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Score {self.score} for {self.entry.date}"


class MonthlyScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    score = models.FloatField()

    class Meta:
        unique_together = ("user", "year", "month")

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}: {self.score}"


class YearlyScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    score = models.FloatField()

    class Meta:
        unique_together = ("user", "year")

    def __str__(self):
        return f"{self.user.username} - Year {self.year}: {self.score}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)  # 1 to 5
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.rating} stars"
def profile_upload_path(instance, filename):
    return f"profile/{instance.user.id}/{filename}"

def header_upload_path(instance, filename):
    return f"profile/{instance.user.id}/header/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=300, blank=True)

    profile_image = CloudinaryField(
        'profile_image',
        blank=True,
        null=True
    )
    header_image = CloudinaryField(
        'header_image',
        blank=True,
        null=True
    )


    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"





