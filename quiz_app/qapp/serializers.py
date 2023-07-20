from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from .models import Quiz,Question,Choice,QuizSubmission


User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email","first_name","last_name", "password", "password2"]

    def save(self):
        reg = User(
            username =self.validated_data['username'],
            email = self.validated_data['email'],
            first_name =self.validated_data['first_name'],
            last_name =self.validated_data['last_name'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Password should match'})
        reg.set_password(password)
        reg.save()
        return reg

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'options', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'qtn', 'choices']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True) 
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Quiz
        fields = ['title', 'topic', 'difficulty_level', 'created_by', 'created_at', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            choices_data = question_data.pop('choices')
            question = Question.objects.create(quiz=quiz, **question_data)

            for choice_data in choices_data:
                Choice.objects.create(qtn=question, **choice_data)

        return quiz


class QuizSubmissionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') 
    quiz_title = serializers.ReadOnlyField(source='quiz.title')


    class Meta:
        model = QuizSubmission
        fields = ['id', 'user', 'quiz','quiz_title', 'score', 'submission_date']
        read_only_fields = ['quiz', 'score', 'submission_date'] 




class QuizListSerializer(serializers.ModelSerializer):

    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Quiz
        fields = ['title','difficulty_level', 'created_by', 'created_at', ]


class QuizAnalyticsSerializer(serializers.Serializer):

    quiz_overview = serializers.DictField()
    performance_metrics = serializers.DictField()
    most_answered_questions = serializers.ListField(child=serializers.CharField())
    least_answered_questions = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = ['quiz_overview', 'performance_metrics', 'most_answered_questions', 'least_answered_questions']


class UserProfileSerializer(serializers.ModelSerializer):
    created_quizzes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'created_quizzes']

    def get_created_quizzes(self, user):
        return Quiz.objects.filter(created_by=user).values_list('title', flat=True)