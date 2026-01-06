# from ecom_api.accounts.models import LoginHistory
import os
import uuid
from django.contrib.messages.api import success
from ipaddress import ip_address
from django.shortcuts import render
from rest_framework.response import Response
from .models import User, EmailVerificationToken, LoginHistory, UserSession
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    EmailVerificationSerializer,
    UserSerializer,
    ResendVerificationSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    UserUpdateSerializer,
    AddressSerializer,
)
from rest_framework.decorators import api_view
from rest_framework import status, parsers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import (
    permission_classes,
    authentication_classes,
    throttle_classes,
    parser_classes,
)
from .utils import (
    send_verification_email,
    send_wellcome_email,
    send_password_change_confirmation_email,
    send_password_reset_email,
)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from accounts.models import Address

# Create your views here.


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        email_sent = send_verification_email(user, request)
        if email_sent:
            return Response(
                {
                    "success": True,
                    "code": "success",
                    "data": {
                        "email": user.email,
                    },
                    "message": "User register successfully. Please check your email to verify your account",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "User register successfully but email verification failed. Please request a new verification email.",
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response(
            {
                "success": False,
                "message": "Invalid email or password",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {
                "success": False,
                "message": "Account is inactive",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    refresh = RefreshToken.for_user(user)

    UserSession.objects.create(
        user=user,
        session_key=refresh["jti"],
        ip_address=request.META.get("REMOTE_ADDR"),
        device_info=request.META.get("HTTP_USER_AGENT", ""),
        is_active=True,
    )

    return Response(
        {
            "success": True,
            "message": "User logged in successfully",
            "code": "success",
            "data": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "PATCH", "PUT"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    if request.method == "GET":
        try:
            serializer = UserSerializer(request.user)
            return Response(
                {
                    "sucess": True,
                    "message": "Profile retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve profile",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method in ["PATCH", "PUT"]:
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Profile updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update profile.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify user email using token sent via email.
    Handles various error cases with proper error messages.
    """
    # Check if token is provided
    if "token" not in request.data:
        return Response(
            {
                "success": False,
                "message": "Token is required",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = EmailVerificationSerializer(data=request.data)

    if not serializer.is_valid():
        # Handle validation errors (e.g., invalid UUID format)
        errors = serializer.errors
        if "token" in errors:
            return Response(
                {
                    "success": False,
                    "message": "Invalid token format. Please use the link from your verification email.",
                    "code": "invalid_token_format",
                    "details": errors["token"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "success": False,
                "message": "Validation failed",
                "code": "validation_error",
                "details": errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    token_value = serializer.validated_data["token"]

    try:
        token = EmailVerificationToken.objects.get(token=token_value)
        user = token.user

        # Check if token is already used
        if token.is_used:
            return Response(
                {
                    "success": False,
                    "message": "This verification link has already been used.",
                    "code": "token_already_used",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if token is expired
        if not token.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "This verification link has expired. Please request a new verification email.",
                    "code": "token_expired",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if email is already verified
        if user.is_email_verified:
            return Response(
                {
                    "success": False,
                    "message": "Your email is already verified.",
                    "code": "email_already_verified",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark token as used
        token.is_used = True
        token.save()

        # Mark user email as verified
        user.is_email_verified = True
        user.save()

        return Response(
            {
                "success": True,
                "message": "Email verified successfully",
                "data": {
                    "user": UserSerializer(user).data,
                },
            },
            status=status.HTTP_200_OK,
        )

    except EmailVerificationToken.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Invalid token",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "message": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    token_value = serializer.validated_data["token"]

    try:
        token = EmailVerificationToken.objects.get(token=token_value)
        user = token.user

        # Check if token is already used
        if token.is_used:
            return Response(
                {
                    "success": False,
                    "message": "This verification link has already been used.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if token is expired
        if not token.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "This verification link has expired. Please request a new verification email.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if email is already verified
        if user.is_email_verified:
            return Response(
                {
                    "success": False,
                    "message": "Your email is already verified.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark token as used
        token.is_used = True
        token.save()

        # Mark user email as verified
        user.is_email_verified = True
        user.save()

        # Send welcome email
        send_wellcome_email(user)

        return Response(
            {
                "success": True,
                "message": "Email verified successfully",
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_email_verified": user.is_email_verified,
                },
            },
            status=status.HTTP_200_OK,
        )

    except EmailVerificationToken.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Invalid verification token. The token may not exist or has been deleted.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        print(f"Error verifying email: {e}")
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred while verifying your email. Please try again later.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification_email(request):
    serializer = ResendVerificationSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        # Send new verification email
        email_sent = send_verification_email(user, request)
        if email_sent:
            return Response(
                {
                    "success": True,
                    "message": "Verification email sent successfully. Please check your inbox",
                    "email": user.email,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "success": False,
                    "message": "Failed to send verification email",
                    "email": user.email,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.
    Requires old_password, new_password, and confirm_password.
    Invalidates all other active sessions and sends confirmation email.
    """
    serializer = ChangePasswordSerializer(
        data=request.data, context={"request": request}
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = request.user
        new_password = serializer.validated_data["new_password"]
        # change password
        user.set_password(new_password)
        user.save()
        # Invalidate all sessions except current
        user.user_sessions.exclude(session_key=request.session.session_key).update(
            is_active=False
        )
        # log the password change
        LoginHistory.objects.create(
            user=user,
            ip_address=request.META.get("REMOTE_ADDR"),
            device_info=request.META.get("HTTP_USER_AGENT"),
            status="success",
        )
        # Send confirmation email
        send_password_change_confirmation_email(user)
        return Response(
            {
                "message": "Password changed successfully. You will be logged out from all other devices.",
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print(f"Error changing password: {e}")
        return Response(
            {
                "message": "Failed to change password",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def forgot_password(request):
    """
    Request password reet email
    """
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        # create reset token
        reset_token = serializer.save()
        # rate limit
        email = serializer.validated_data["email"]
        cache_key = f"forgot_password_{email}"
        reset_attempts = cache.get(cache_key, 0)

        if reset_attempts >= 3:
            return Response(
                {
                    "message": "Too many attempts. Please try again after 5 minutes.",
                    "email": email,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        # incriment attempts
        cache.set(cache_key, reset_attempts + 1, timeout=300)

        # Send password reset email
        send_password_reset_email(User.objects.get(email=email), reset_token)

        return Response(
            {"message": "Password reset email sent. Please check your inbox"}
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["post"])
@permission_classes([IsAuthenticated])
def logout_all(request):
    """
    Logout all devices
    """
    active_sessions = request.user.user_sessions.filter(is_active=True)
    print(active_sessions.exists())
    if not active_sessions.exists():
        return Response({"success": False, "message": "No active sessions found."})

    active_sessions.update(is_active=False)
    return Response(
        {"success": True, "message": "Logged out from all other devices successfully."}
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user
    # partial=True allows sending only some fields for updates
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {
            "success": False,
            "message": "Failed to update profile.",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([parsers.MultiPartParser])
def manage_profile_avatar(request):
    """
    Manage profile avatar: Upload (POST) or Delete (DELETE)
    POST /api/auth/profile/avatar/
    DELETE /api/auth/profile/avatar/
    """
    try:
        user = request.user

        if request.method == "DELETE":
            if not user.profile_image:
                return Response(
                    {
                        "success": False,
                        "message": "No avatar found for this user",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                if user.profile_image:
                    default_storage.delete(user.profile_image.name)
                user.profile_image = None
                user.save()
                return Response(
                    {
                        "success": True,
                        "message": "Profile image deleted successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                print(f"Error deleting avatar: {e}")
                return Response(
                    {
                        "success": False,
                        "message": "Failed to delete avatar",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Check if file is provided
        if "avatar" not in request.FILES:
            return Response(
                {
                    "success": False,
                    "message": "No file provided",
                    "code": "no_file_provided",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        avatar_file = request.FILES["avatar"]

        # Validate file type
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/jpg",
            "image/gif",
            "image/webp",
        ]
        if avatar_file.content_type not in allowed_types:
            return Response(
                {
                    "success": False,
                    "message": "Invalid file type. Only JPEG, PNG, GIF, and WEBP are allowed.",
                    "code": "invalid_file_type",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024
        if avatar_file.size > max_size:
            return Response(
                {
                    "success": False,
                    "message": "File size too large. Maximum size is 5MB.",
                    "code": "file_too_large",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate unique filename
        file_extension = os.path.splitext(avatar_file.name)[1]
        filename = f"avatars/user_{user.id}/{uuid.uuid4()}{file_extension}"

        # Delete old avatar if exists
        if user.profile_image:
            try:
                default_storage.delete(user.profile_image.name)
            except Exception as e:
                print(f"Error deleting old avatar: {e}")

        # Save to S3 using Django's storage backend
        saved_path = default_storage.save(filename, ContentFile(avatar_file.read()))
        avatar_url = default_storage.url(saved_path)

        # Update user profile
        user.profile_image = saved_path
        user.save()

        return Response(
            {
                "success": True,
                "message": "Profile avatar uploaded successfully",
                "data": {
                    "avatar_url": avatar_url,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(f"Error uploading avatar: {e}")
        return Response(
            {
                "success": False,
                "message": "Failed to upload avatar",
                "code": "upload_failed",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_profile_cover(request):
    """
    Manage profile cover image: Upload (POST) or Delete (DELETE)
    POST /api/auth/profile/cover/
    DELETE /api/auth/profile/cover/
    """
    try:
        user = request.user
        if request.method == "DELETE":
            if not user.cover_image:
                return Response(
                    {
                        "success": False,
                        "message": "No cover image found for this user",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                if user.cover_image:
                    default_storage.delete(user.cover_image.name)
                user.cover_image = None
                user.save()
                return Response(
                    {
                        "sucess": True,
                        "message": "Cover image deleted successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                print(f"Error deleting cover image: {e}")
                return Response(
                    {
                        "success": False,
                        "message": "Failed to delete cover image",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        # Handle POST (Upload)
        # Check if file is provided
        if "cover" not in request.FILES:
            return Response(
                {
                    "success": False,
                    "message": "No file provided",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        cover_file = request.FILES["cover"]
        # Validate file type
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/jpg",
            "image/gif",
            "image/webp",
        ]

        if cover_file.content_type not in allowed_types:
            return Response(
                {
                    "success": False,
                    "message": "Invalid file type. Only JPEG, PNG, GIF, and WEBP are allowed.",
                    "code": "invalid_file_type",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if cover_file.size > 5 * 1024 * 1024:
            return Response(
                {
                    "success": False,
                    "message": "File size too large. Maximum size is 5MB.",
                    "code": "file_too_large",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        file_extension = os.path.splitext(cover_file.name)[1]
        filename = f"covers/user_{user.id}/{uuid.uuid4()}{file_extension}"
        if user.cover_image:
            try:
                default_storage.delete(user.cover_image.name)
            except Exception as e:
                print(f"Error deleting old cover image: {e}")
        saved_path = default_storage.save(filename, ContentFile(cover_file.read()))
        cover_url = default_storage.url(saved_path)
        user.cover_image = saved_path
        user.save()
        return Response(
            {
                "success": True,
                "message": "Cover image uploaded successfully",
                "data": {
                    "cover_url": cover_url,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(f"Error uploading cover image: {e}")
        return Response(
            {
                "success": False,
                "message": "Failed to upload cover image",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def address_list(request):
    """
    List all addresses or create a new one.
    GET /api/auth/addresses/
    POST /api/auth/addresses/
    """
    if request.method == "GET":
        addresses = request.user.addresses.all()
        serializer = AddressSerializer(addresses, many=True)
        return Response(
            {
                "success": True,
                "message": "Addresses retrieved successfully",
                "data": serializer.data,
            }
        )
    elif request.method == "POST":
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {
                    "success": True,
                    "message": "Address created successfully",
                    "data": serializer.data,
                }
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create address",
                "code": "address_creation_failed",
            }
        )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def address_detail(request, pk):
    """
    Retrieve, update or delete a specific address.
    GET /api/auth/addresses/<id>/
    PUT /api/auth/addresses/<id>/
    DELETE /api/auth/addresses/<id>/
    """
    address = get_object_or_404(Address, pk=pk, user=request.user)
    print(address)

    if request.method == "GET":
        serializer = AddressSerializer(address)
        return Response(
            {
                "success": True,
                "message": "Address retrieved successfully",
                "data": serializer.data,
            }
        )
    elif request.method == "PUT":
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Address updated successfully",
                    "data": serializer.data,
                }
            )
        return Response(
            {
                "success": False,
                "message": "Failed to update address",
                "code": "address_update_failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    elif request.method == "DELETE":
        address.delete()
        return Response(
            {
                "success": True,
                "message": "Address deleted successfully",
            }
        )
