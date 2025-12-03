from django.urls import path 
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)   




urlpatterns = [
    path('register/',views.register_user,name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('login/',views.login_user,name='login'),
    path('profile/', views.get_user_profile, name='profile'),
    path('token/refresh/',TokenRefreshView.as_view(),name='refresh_token'),
    path('token/verify/',TokenVerifyView.as_view(),name='token_verify'),
    path('resend-verification-email/', views.resend_verification_email, name='resend_verification'),
    
]
