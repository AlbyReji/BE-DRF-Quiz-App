from django.contrib import admin
from qapp.models import User,Quiz,Question,Choice,QuizSubmission


admin.site.register(Quiz)
admin.site.register(User)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuizSubmission)
