from rest_framework import serializers
from .models import User , UserProfile, Address, EmailVerificationToken, PasswordResetToken
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

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

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return attrs
        
        
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user=User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField()
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields='__all__'


       



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model=Address
        fields='__all__'
        read_only_fields=('user','created_at','updated_at')   

class UserSerializer(serializers.ModelSerializer):
    profile=UserProfileSerializer(read_only=True)
    addresses=AddressSerializer(read_only=True, many=True)
    class Meta:
        model=User
        fields=('id','email','first_name','last_name','phone_number','role','is_email_verified','is_phone_verified','profile','addresses','created_at','updated_at')          

class EmailVerificationSerializer(serializers.Serializer):
    token=serializers.UUIDField()
    def validate_token(self,value):
        try:
            token=EmailVerificationToken.objects.get(token=value)
            if not token.is_valid():
                raise serializers.ValidationError("Verification token has expired or already been used.")    
            return value
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")


class ResendVerificationSerializer(serializers.Serializer):
    email=serializers.EmailField()
    def validate_email(self,value):
        try:
            user=User.objects.get(email=value)
            if user.is_email_verified:
                raise serializers.ValidationError("Email already verified.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")    



class ChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(required=True,write_only=True)
    new_password=serializers.CharField(required=True,write_only=True)
    confirm_password=serializers.CharField(required=True,write_only=True)

    def validate(self,attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        
        if(attrs['old_password']==attrs['new_password']):
            raise serializers.ValidationError("New password can not be same.")
        validate_password(attrs['new_password'])
        return attrs


    def validate_old_password(self,value):
        user=self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("old password is incorrect.")
        return value



class ForgotPasswordSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    def validate_email(self,value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

    def save(self):
        email=self.validated_data['email']
        user=User.objects.get(email=email)
        # Invalidate existing tokens
        PasswordResetToken.objects.filter(user=user,is_used=False).update(is_used=True)
        # Create new token
        token=PasswordResetToken.objects.create(user=user)
        return token

class UserUpdateSerializer(serializers.ModelSerializer):
    profile= UserProfileSerializer(required=False)
    class Meta:
        model=User
        fields=('first_name','last_name','phone_number','profile','date_of_birth','gender') 

    def update(self, instance, validated_data):
        # Extract profile data data if present
        profile_data=validated_data.pop('profile', None);
        for attr, value in validated_data.items():
            setattr(instance,attr,value) 
            instance.save()
       # Update UserProfile fields
        if profile_data:
            profile, created=UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile,attr,value) 
            profile.save() 
        return instance

class ProfileAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('profile_image')

    def validate_profile_image(self, value):
        if(value.size> 5*1024*1024):
            raise serializers.ValidationError("Profile image size should be less than 5MB.")
        return value



class AvatarUploadSerializer(serializers.ModelSerializer):
    avatar=serializers.ImageField(
        required=True,
        max_length=100,
        allow_empty_file=False,
        help_text="Profile avatar image (max 5MB)"

    )
    def validate_avatar(self,value):
         # Validate file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError("Invalid file extension. Only JPG, JPEG, PNG, GIF, and WEBP are allowed.")
        if value.size > 5*1024*1024:
            raise serializers.ValidationError("Profile image size should be less than 5MB.")
        return value
        
    


        



        





    
        

            