





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


def send_verification_email(user,request):
    try:
        