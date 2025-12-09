from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailVerificationToken
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
