from django.shortcuts import render
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework import status



# Create your views here.


@api_view(['POST'])

def register_user(request):
    serializer=UserSerializer(data=request.data)
    
    
    
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
