from django.shortcuts import render

from .serializers import (UserRegisterSerializer,
                            AdminSerializer,
                            QuizSerializer,
                            QuestionSerializer,
                            QuizSubmissionSerializer ,
                            QuizListSerializer,
                            QuizAnalyticsSerializer,
                            UserProfileSerializer)

from .models import (Quiz,
                        User,
                        Question,
                        Choice,
                        QuizSubmission)


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView 
from rest_framework import generics,serializers
from rest_framework.generics import  RetrieveAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Max, Min, Count

from .pagination import NumberPagination






class Register(APIView):

    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'message:User created'
            refresh = RefreshToken.for_user(account)
        else:
            data = serializer.errors
        return Response(data)

class AdminRegister(APIView):

    permission_classes = [IsAdminUser]
    
    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'message:User created'
            refresh = RefreshToken.for_user(account)
        else:
            data = serializer.errors
        return Response(data)


class AdminList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAdminUser]
    authentication_classes=[JWTAuthentication]
    pagination_class = NumberPagination



class AdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "User deleted successfully."})
        except NotFound:
            return Response({"message": "User not found."})


class QuizCreate(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)



class QuizTaking(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSubmissionSerializer

    def get_quiz_instance(self, quiz_id):
        try:
            return Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return None

    def create(self, request, quiz_id, *args, **kwargs):
        quiz = self.get_quiz_instance(quiz_id)
        if not quiz:
            return Response({"detail": "Quiz not found."})

        user = request.user

        if QuizSubmission.objects.filter(user=user, quiz=quiz).exists():
            return Response({"detail": f"hi,{user.username} You have already submitted this quiz."})
        data = request.data
        score = 0

        for question_id, selected_choice_id in data.items():
            try:
                question = quiz.questions.get(pk=question_id)
                selected_choice = question.choices.get(pk=selected_choice_id)

                if selected_choice.is_correct:
                    score += 1
            except (Question.DoesNotExist, Choice.DoesNotExist):
                return Response({"detail": "Invalid question or choice data."})

        total_questions = quiz.questions.count()
        percentage_score = (score / total_questions) * 100

        quiz_submission = QuizSubmission.objects.create(user=user, quiz=quiz, score=percentage_score)

        return Response({"detail": f"Hey ,{user.username}You scored {percentage_score}% on the quiz '{quiz.title}'."})



class QuizResult(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        return QuizSubmission.objects.filter(user=user)


class QuizList(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['topic', 'difficulty_level']
    ordering_fields = ['created_at']
    pagination_class = NumberPagination



class QuizAnalytics(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizAnalyticsSerializer

    def get(self, request, *args, **kwargs):
        total_quizzes = Quiz.objects.count()
        total_quiz_takers = QuizSubmission.objects.values('user').distinct().count()
        average_quiz_score = QuizSubmission.objects.aggregate(Avg('score'))['score__avg']

        passed_quiz_takers = QuizSubmission.objects.filter(score__gte=40).values('user').distinct().count()
        pass_percentage = (passed_quiz_takers / total_quiz_takers) * 100

        quizzes = Quiz.objects.all()
        performance_metrics = []
        for quiz in quizzes:
            quiz_submissions = QuizSubmission.objects.filter(quiz=quiz)
            average_score = quiz_submissions.aggregate(Avg('score'))['score__avg']
            highest_score = quiz_submissions.aggregate(Max('score'))['score__max']
            lowest_score = quiz_submissions.aggregate(Min('score'))['score__min']
            performance_metrics.append({
                'quiz_id': quiz.id,
                'quiz_title': quiz.title,
                'average_score': average_score,
                'highest_score': highest_score,
                'lowest_score': lowest_score,
            })

        performance_metrics = [metric for metric in performance_metrics if metric['highest_score'] is not None]
        if performance_metrics:
            highest_score_quiz = max(performance_metrics, key=lambda x: x['highest_score'])
            lowest_score_quiz = min(performance_metrics, key=lambda x: x['lowest_score'])
        else:
            highest_score_quiz = {'quiz_title': None, 'highest_score': None}
            lowest_score_quiz = {'quiz_title': None, 'lowest_score': None}

        questions = Question.objects.all()
        question_statistics = []
        for question in questions:
            total_answers = Choice.objects.filter(qtn=question).count()
            question_statistics.append({
                'question_id': question.id,
                'question_text': question.qtn,
                'total_answers': total_answers,
            })

        most_answered_questions = sorted(question_statistics, key=lambda x: x['total_answers'], reverse=True)[:2]
        least_answered_questions = sorted(question_statistics, key=lambda x: x['total_answers'])[:2]

        analytics_data = {
            'quiz_overview': {
                'no_of_quizzes': total_quizzes,
                'no_of_quiz_takers': total_quiz_takers,
                'average_quiz_score': average_quiz_score,
                'pass_percentage': pass_percentage,

            },
            'performance_metrics': {
                'average_score': average_quiz_score,
                'highest_score': highest_score_quiz['highest_score'],
                'lowest_score': lowest_score_quiz['lowest_score'],
            },
            'most_answered_questions': [q['question_text'] for q in most_answered_questions],
            'least_answered_questions': [q['question_text'] for q in least_answered_questions],
        }

        serializer = self.serializer_class(data=analytics_data)
        serializer.is_valid()
        return Response(serializer.data)


class UserProfile(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

