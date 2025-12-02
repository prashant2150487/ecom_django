from django.shortcuts import render
from rest_framework.response import Response
from .models import User
from .serializers import UserRegisterSerializer,UserLoginSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from .utils import send_verification_email




# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer=UserRegisterSerializer(data=request.data)

    if serializer.is_valid():
        user=serializer.save()
        email_sent=send_verification_email(user,request)
        if email_sent:
            return Response({"message":"User register successfully. Please check your email to verify your account",
            "email":user.email}, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message":"User register successfully but email verification failed. Please request a new verification email.",
                "email":user.email
            }, status=status.HTTP_201_CREATED)    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer=UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        email=serializer.validated_data['email']
        password=serializer.validated_data['password']
        user=authenticate(request, email=email, password=password)
        if user:
            refresh=RefreshToken.for_user(user)
            return Response({
                'user':UserSerializer(user).data,
                'refresh':str(refresh),
                'access':str(refresh.access_token)
            },
            status=status.HTTP_200_OK
            )


        return Response({"error":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)     

@api_view(['GET'])
def get_user_profile(request):
    serializer=UserProfileSerializer(request.user)
    return Response(serializer.data,status=status.HTTP_200_OK)



@api_view(['POST'])
def verify_email(request):
    serializer=EmailVerificationSerializer(data=request.data)
    if serializer.is_valid():
        token=serializer.validated_data['token']
        try:
            token=EmailVerificationToken.objects.get(token=token_value)
            user=token.user

            # Mark token as used    
            token_is_user=True
            token.save()

            # Mark user email as verified
            
            user.is_email_verified=True
            user.save()
             # Send welcome email
            send_wellcome_email(user)
            return Response({
                "message":"Email verified successfully",
                "user":{
                    "email":user.email,
                    "first_name":user.first_name,
                    "last_name":user.last_name,
                    "is_email_verified":user.is_email_verified
                }
            }, status=status.HTTP_200_OK)
        except EmailVerificationToken.DoesNotExist:
            return Response({"error":"Invalid verification token"}, status=status.HTTP_400_BAD_REQUEST)    

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    serializer=ResendVerificationSerializer(data=request.data)
    if serializer.is_valid():
        email=serializer.validated_data['email']
        user=User.objects.get(email=email)
        # Send new verification email
        email_sent=send_verification_email(user,request)
        if email_sent:
            return Response({
                "message":"Verification email sent successfully. Please check your inbox",
                "email":user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message":"Failed to send verification email",
                "email":user.email
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
       

    




    
