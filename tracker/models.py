from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# ---------------------------------------------------------
# 1. Criteria (max 5 per user)
# ---------------------------------------------------------
class Criterion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="criteria")
    name = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=0)  # For sorting criteria

    class Meta:
        ordering = ["order"]
        unique_together = ("user", "order")

    def __str__(self):
        return f"{self.user.username} - {self.name}"


# ---------------------------------------------------------
# 2. Daily Entry (ratings + descriptions for 5 criteria)
# ---------------------------------------------------------
class DailyEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entries")
    date = models.DateField()

    # Example stored JSON:
    # ratings = {"Study": 4, "Coding": 3}
    # descriptions = {"Study": "Read OS chapter", "Coding": "Solved 2 problems"}
    ratings = models.JSONField()
    descriptions = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


# ---------------------------------------------------------
# 3. Daily Score (from Gemini API)
# ---------------------------------------------------------
class DailyScore(models.Model):
    entry = models.OneToOneField(DailyEntry, on_delete=models.CASCADE, related_name="score")
    score = models.FloatField()  # Example: 113.0
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Score {self.score} for {self.entry.date}"


# ---------------------------------------------------------
# 4. Monthly Score (average of daily scores)
# ---------------------------------------------------------
class MonthlyScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    score = models.FloatField()

    class Meta:
        unique_together = ("user", "year", "month")

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}: {self.score}"


# ---------------------------------------------------------
# 5. Yearly Score (average of monthly scores)
# ---------------------------------------------------------
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


class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = CloudinaryField(
        'achievement_image',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
class AchievementLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')
class AchievementComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
