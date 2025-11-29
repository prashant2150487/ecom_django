from django.shortcuts import render
from rest_framework.response import Response
from .models import User
from .serializers import UserRegisterSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes




# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer=UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"User register successfully"}, status=status.HTTP_201_CREATED)
    
    
    
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
