from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]



class Quiz(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes_created')
    created_at = models.DateTimeField(auto_now_add=True)
    topic = models.CharField(max_length=255)
    difficulty_level = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    qtn = models.TextField()

    def __str__(self):
        return self.qtn

class Choice(models.Model):
    qtn = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    options = models.TextField()
    is_correct = models.BooleanField(default=False)


class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
    