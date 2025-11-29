from rest_framework import serializers
from .models import User 
from django.contrib.auth.password_validation import validate_password
class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=('email','first_name','last_name','password','password_confirm','phone_number')
        
        
    def validate(self,attrs):
        if(attrs['password']!= attrs['password_confirm']):
            raise serializers.ValidationError({'password': "Password did't match."})
        return attrs
        
        
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user=User.objects.create_user(**validated_data)
        return user
        

            