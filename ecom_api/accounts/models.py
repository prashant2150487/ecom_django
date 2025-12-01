from secrets import choice
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from .managers import UserManager
import uuid


# Phone number validator - reusable across models
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
)


# Create your models here.



class User(AbstractUser):
    """
    Custom User model that uses email instead of username for authentication.
    Extends Django's AbstractUser with additional fields for e-commerce functionality.
    """
    USER_ROLES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
        ('staff', 'Staff')
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )
    
    # Remove username field from AbstractUser
    username = None
    
    # Core fields
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=17, validators=[phone_regex], blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    
    # Profile fields
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Verification flags
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_role_display_name(self):
        """Returns the display name for the user's role."""
        return dict(self.USER_ROLES).get(self.role, 'Customer')

class UserProfile(models.Model):
    """Extended user profile with preferences and social links."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_language = models.CharField(max_length=20, default='en')
    preferred_currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    newsletter_subscription = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=False)
    profile_visibility = models.BooleanField(default=True)
    show_email = models.BooleanField(default=True)
    show_phone_number = models.BooleanField(default=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email}'s profile"

class Address(models.Model):
    """User shipping and billing addresses."""
    ADDRESS_TYPES = (
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
        ('both', 'Both'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='shipping')
    label = models.CharField(max_length=50, blank=True, null=True)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=17, validators=[phone_regex], blank=True, null=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    postal_code = models.CharField(max_length=20)
    is_default_shipping = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'addresses'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"
    


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.CharField(default=uuid.uuid4, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_used=models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verifications+tokens'
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
    
    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset')
    token = models.UUIDField(default=uuid.uuid4,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_used=models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Password Reset'
        verbose_name_plural = 'Password Resets'
    
    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sessions')
    session_key = models.CharField(max_length=40,db_index=True)
    device_info = models.TextField(blank=True,null=True)
    ip_address = models.GenericIPAddressField(blank=True,null=True)
    city=models.CharField(max_length=100,blank=True,null=True)
    country=models.CharField(max_length=100,blank=True,null=True)
    login_at=models.DateTimeField(auto_now_add=True)
    last_activity=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    class Meta:
        db_table= 'user_sessions'

    def __str__(self):
        return f"{self.user.email} - {self.login_at}"    

class LoginHistory(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE,related_name='login_history')
    login_at=models.DateTimeField(auto_now_add=True)
    ip_address=models.GenericIPAddressField(blank=True,null=True)
    device_info=models.TextField(blank=True,null=True)
    city=models.CharField(max_length=100,blank=True,null=True)
    country=models.CharField(max_length=100,blank=True,null=True)
    status=models.CharField(max_length=20,choices=(('success','Success'),('failed','Failed' )))
    failure_reason=models.TextField(blank=True,null=True)


    class Meta:
        db_table='login_history'
        verbose_name_plural='Login Histories'

    def __str__(self):
        return f"{self.user.email} - {self.login_at}"  
        
          

    
