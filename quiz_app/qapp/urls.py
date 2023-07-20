from django.urls import path
from .import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/',views.Register.as_view(),name = "register"),
    path('adminregister/',views.AdminRegister.as_view(),name = "adminregister"),
    path('adminlist/', views.AdminList.as_view(), name='adminlist'),
    path('adminlist/<int:pk>/',views.AdminDetailView.as_view(), name='adminlist'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('quizcreate/',views.QuizCreate.as_view(),name = "quizcreate"),
    path('quiztaking/',views.QuizTaking.as_view(),name = "quiztaking"),
    path('quiztaking/<int:quiz_id>/',views.QuizTaking.as_view(), name='quiz-taking'),
    path('quizresult/',views.QuizResult.as_view(),name = "quizresult"),
    path('quizlist/',views.QuizList.as_view(),name = "quizlist"),
    path('quizanalytics/',views.QuizAnalytics.as_view(),name = "quizanalytics"),
    path('userprofile/',views.UserProfile.as_view(),name = "userprofile"),

]