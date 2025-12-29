from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailVerificationToken
from botocore.exceptions import ClientError
import uuid
import os   
import boto3
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_verification_token(user):
    """Generate email verification token for user"""
    # Invalidate any existing unused tokens
    EmailVerificationToken.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)
    
    # Create new token
    token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=24)
    )
    return token


def send_verification_email(user, request):
    """Send email verification email to user"""
    try:
        # Generate verification token
        token = generate_verification_token(user)
        print(token,"token")
        
        # Build verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"
        
        # Prepare email context
        context = {
            'user': user,
            'verification_url': verification_url,
            'expiry_hours': 24
        }
        
        # Render email templates
        html_message = render_to_string('emails/verification_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Verify your email address',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        # import traceback
        # traceback.print_exc()
        return False
    
def send_wellcome_email(user):
    try:
        context={
            'user':user
        }
        html_message=render_to_string('accounts/welcome_email.html',context)
        plain_message=strip_tags(html_message)
        send_mail(
            subject='Wellcome to E-commerce Platefrom',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
    
def send_password_change_confirmation_email(user):
    """
    Send email confirmation when password is changed.
    """
    try:
        context = {
            'user': user
        }
        html_message = render_to_string('emails/password_change_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Password Changed Successfully',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending password change confirmation email: {e}")
        return False
    
def send_password_reset_email(user, reset_token):
    """
    Send password reset email to user
    """
    try:
        # Build reset URL
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
        
        context = {
            'user': user,
            'reset_link': reset_link,
            'expiry_hours': 24,
            'support_email': settings.DEFAULT_FROM_EMAIL
        }
        
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Reset Your Password',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False



def get_s3_client():
    """Get S3 client instance"""
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

def upload_to_s3(file_content, folder, filename=None, content_type=None):
    """
    Upload file to S3 bucket
    
    Args:
        file_content: File content (bytes)
        folder: Folder path in S3 (e.g., 'avatars/user_1/')
        filename: Optional filename (will generate UUID if not provided)
        content_type: Optional content type
    
    Returns:
        tuple: (s3_key, s3_url)
    """
    s3_client = get_s3_client()
    
    if not filename:
        filename = f"{uuid.uuid4()}"
    
    # Ensure folder ends with /
    if not folder.endswith('/'):
        folder = f"{folder}/"
    
    s3_key = f"{folder}{filename}"
    
    extra_args = {}
    if content_type:
        extra_args['ContentType'] = content_type
    
    s3_client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=s3_key,
        Body=file_content,
        **extra_args
    )
    
    # Generate URL
    s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
    
    return s3_key, s3_url

def delete_from_s3(s3_key):
    """
    Delete file from S3 bucket
    
    Args:
        s3_key: S3 key to delete
    
    Returns:
        bool: True if deleted, False if not found
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=s3_key
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False  # File already doesn't exist
        raise

def get_presigned_url(s3_key, expiration=3600):
    """
    Generate a presigned URL for S3 object
    
    Args:
        s3_key: S3 object key
        expiration: URL expiration time in seconds (default 1 hour)
    
    Returns:
        str: Presigned URL
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None

def generate_avatar_key(user_id, file_extension):
    """Generate S3 key for user avatar"""
    return f"avatars/user_{user_id}/{uuid.uuid4()}{file_extension}"

def generate_cover_key(user_id, file_extension):
    """Generate S3 key for user cover image"""
    return f"covers/user_{user_id}/{uuid.uuid4()}{file_extension}"

