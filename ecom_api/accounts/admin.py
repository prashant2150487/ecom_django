from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin




from .models import User, UserProfile, Address, EmailVerificationToken, PasswordResetToken, UserSession, LoginHistory



# ============================
# ✅ USER PROFILE INLINE
# ============================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

# ============================
# ✅ ADDRESS INLINE
# ============================
class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    
# ============================
# ✅ CUSTOM USER ADMIN
# ============================


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-created_at',)
    list_display = (
        'email',
        'full_name',
        'role',
        'is_staff',
        'is_active',
        'is_email_verified',
        'created_at'
    )

    list_filter = (
        'role',
        'is_staff',
        'is_active',
        'is_email_verified',
    )

    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        ('Authentication', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender')}),
        ('Profile Images', {'fields': ('profile_image', 'cover_image', 'bio')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_superuser', 'is_active')}),
        ('Verification', {'fields': ('is_email_verified', 'is_phone_verified')}),
        ('Important Dates', {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at', 'last_login')

    inlines = [UserProfileInline, AddressInline]

    USERNAME_FIELD = 'email'
 

# ============================
# ✅ USER PROFILE ADMIN
# ============================

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = (
#         'user',
#         'preferred_language',
#         'preferred_currency',
#         'timezone',
#         'newsletter_subscription',
#     )
#     list_filter = ('newsletter_subscription',)
#     search_fields = ('user__email',)


# ============================
# ✅ ADDRESS ADMIN
# ============================

# @admin.register(Address)
# class AddressAdmin(admin.ModelAdmin):
#     list_display = (
#         'user',
#         'full_name',
#         'city',
#         'state',
#         'country',
#         'is_default_shipping',
#         'is_default_billing',
#         'created_at'
#     )

#     list_filter = ('country', 'is_default_shipping', 'is_default_billing')
#     search_fields = ('full_name', 'city', 'user__email')


# ============================
# ✅ EMAIL VERIFICATION TOKEN
# ============================
@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display =(
        'user',
        'token',
        'is_used',
        'expires_at',
        'created_at'
    )
    list_filter = ('is_used',)
    
    
    
    

# @admin.register(EmailVerificationToken)
# class EmailVerificationTokenAdmin(admin.ModelAdmin):
#     list_display = (
#         'user',
#         'token',
#         'is_used',
#         'expires_at',
#         'created_at'
#     )

#     list_filter = ('is_used',)
#     search_fields = ('user__email', 'token')


# ============================
# ✅ PASSWORD RESET TOKEN
# ============================

# @admin.register(PasswordResetToken)
# class PasswordResetTokenAdmin(admin.ModelAdmin):
#     list_display = (
#         'user',
#         'token',
#         'is_used',
#         'expires_at',
#         'created_at'
#     )

#     list_filter = ('is_used',)
#     search_fields = ('user__email', 'token')


# ============================
# ✅ USER SESSION ADMIN
# ============================

# @admin.register(UserSession)
# class UserSessionAdmin(admin.ModelAdmin):
#     list_display = (
#         'user',
#         'ip_address',
#         'city',
#         'country',
#         'login_at',
#         'last_activity',
#         'is_active'
#     )

#     list_filter = ('is_active', 'country')
#     search_fields = ('user__email', 'ip_address')


# ============================
# ✅ LOGIN HISTORY ADMIN
# ============================

# @admin.register(LoginHistory)
# class LoginHistoryAdmin(admin.ModelAdmin):
#     list_display = (
#         'user',
#         'login_at',
#         'ip_address',
#         'city',
#         'country',
#         'status'
#     )

#     list_filter = ('status', 'country')
#     search_fields = ('user__email', 'ip_address')

