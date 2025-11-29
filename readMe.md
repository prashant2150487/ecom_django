# E-commerce Django Backend with MySQL

A comprehensive e-commerce backend system built with Django and MySQL, featuring product management, user authentication, shopping cart, order processing, and payment integration structure.

## User Review Required

> [!IMPORTANT]
> **Technology Stack Confirmation**
> - **Framework**: Django 5.x with Django REST Framework
> - **Database**: MySQL 8.x
> - **Authentication**: JWT-based authentication
> - **API Style**: RESTful APIs
> - **Payment Gateways**: Multi-gateway support (Stripe, PayPal, Razorpay)
> - **Email Service**: Django email backend with template support
> - **Task Queue**: Celery with Redis for async tasks (email notifications, inventory updates)
> 
> Please confirm if you want any specific versions or additional technologies.

## Proposed Changes

### Project Structure

#### [NEW] Project Initialization
- Initialize Django project named `ecommerce_backend`
- Create multiple Django apps for modular architecture:
  - `accounts` - User authentication and profile management
  - `products` - Product catalog and categories
  - `cart` - Shopping cart functionality
  - `orders` - Order processing and management
  - `payments` - Multi-gateway payment integration
  - `vendors` - Multi-vendor marketplace support
  - `reviews` - Product reviews and ratings
  - `wishlist` - User wishlist functionality
  - `coupons` - Discount and coupon system
  - `inventory` - Stock and warehouse management
  - `notifications` - Email notification system

---

### Database Configuration

#### [NEW] [settings.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/ecommerce_backend/settings.py)
Configure MySQL database connection with proper settings:
- Database engine: `django.db.backends.mysql`
- Connection pooling
- Timezone settings
- Static and media files configuration
- CORS headers for frontend integration
- JWT authentication settings
- REST Framework configuration

---

### Accounts App

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/accounts/models.py)

**Custom User Model** (extending AbstractUser):
- Email as username field (unique, required)
- Phone number with validation
- Date of birth
- Gender (optional)
- User role (customer, admin, vendor, staff)
- Profile image with upload handling
- Cover image (for profile customization)
- Bio/About me text
- Email verification status
- Phone verification status
- Is active, is staff, is superuser flags
- Account creation date
- Last login timestamp
- Updated timestamp

**UserProfile Model** (One-to-One with User):
- Preferred language
- Preferred currency
- Timezone
- Newsletter subscription status
- SMS notification preferences
- Email notification preferences
- Privacy settings (profile visibility, show email, show phone)
- Social media links (Facebook, Twitter, Instagram, LinkedIn)
- Website URL

**Address Model** (Multiple addresses per user):
- User (ForeignKey)
- Address type (shipping, billing, both)
- Label (Home, Office, etc.)
- Full name (recipient name)
- Phone number
- Address line 1 & 2
- City, state, postal code, country
- Is default shipping address
- Is default billing address
- Latitude, longitude (for delivery optimization)
- Created and updated timestamps

**EmailVerificationToken Model**:
- User (ForeignKey)
- Token (unique, auto-generated)
- Created timestamp
- Expires at timestamp
- Is used flag

**PasswordResetToken Model**:
- User (ForeignKey)
- Token (unique, auto-generated)
- Created timestamp
- Expires at timestamp
- Is used flag

**UserSession Model** (Track active sessions):
- User (ForeignKey)
- Session key
- Device information (user agent)
- IP address
- Location (city, country)
- Login timestamp
- Last activity timestamp
- Is active flag

**SocialAccount Model** (for social login):
- User (ForeignKey)
- Provider (Google, Facebook, Apple, etc.)
- Provider user ID
- Access token (encrypted)
- Refresh token (encrypted)
- Token expiry
- Profile data (JSONField)
- Created timestamp

**TwoFactorAuth Model**:
- User (OneToOneField)
- Is enabled flag
- Secret key (encrypted)
- Backup codes (JSONField, encrypted)
- Created timestamp
- Last used timestamp

**LoginHistory Model** (Security audit):
- User (ForeignKey)
- Login timestamp
- IP address
- Device information
- Location
- Status (success, failed)
- Failure reason (if failed)

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/accounts/serializers.py)
- User registration serializer (with email validation, password strength check)
- User login serializer (with rate limiting)
- User profile serializer (with nested UserProfile)
- User profile update serializer
- Password change serializer (requires old password)
- Password reset request serializer
- Password reset confirm serializer
- Email verification serializer
- Phone verification serializer
- Address serializer (CRUD operations)
- Social account serializer
- Two-factor authentication setup serializer
- Two-factor authentication verify serializer
- User session serializer
- Login history serializer
- User preferences serializer
- Privacy settings serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/accounts/views.py)

**Authentication Endpoints**:
- `POST /api/auth/register/` - User registration with email verification
- `POST /api/auth/verify-email/` - Verify email with token
- `POST /api/auth/resend-verification/` - Resend verification email
- `POST /api/auth/login/` - User login (returns JWT tokens + refresh token)
- `POST /api/auth/logout/` - Logout (invalidate token, end session)
- `POST /api/auth/logout-all/` - Logout from all devices
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify if token is valid

**Social Authentication**:
- `POST /api/auth/social/google/` - Login/Register with Google
- `POST /api/auth/social/facebook/` - Login/Register with Facebook
- `POST /api/auth/social/apple/` - Login/Register with Apple
- `GET /api/auth/social/accounts/` - List connected social accounts
- `DELETE /api/auth/social/<provider>/disconnect/` - Disconnect social account

**Password Management**:
- `POST /api/auth/change-password/` - Change password (requires current password)
- `POST /api/auth/forgot-password/` - Request password reset (sends email)
- `POST /api/auth/reset-password/` - Reset password with token
- `POST /api/auth/validate-reset-token/` - Check if reset token is valid
- `POST /api/auth/set-password/` - Set password for social login users

**Profile Management**:
- `GET /api/auth/profile/` - Get current user's full profile
- `PUT /api/auth/profile/` - Update user profile
- `PATCH /api/auth/profile/` - Partial update user profile
- `POST /api/auth/profile/avatar/` - Upload profile image
- `DELETE /api/auth/profile/avatar/` - Remove profile image
- `POST /api/auth/profile/cover/` - Upload cover image
- `DELETE /api/auth/profile/cover/` - Remove cover image
- `GET /api/auth/profile/preferences/` - Get user preferences
- `PUT /api/auth/profile/preferences/` - Update preferences
- `GET /api/auth/profile/privacy/` - Get privacy settings
- `PUT /api/auth/profile/privacy/` - Update privacy settings

**Address Management**:
- `GET /api/auth/addresses/` - List all user addresses
- `POST /api/auth/addresses/` - Add new address
- `GET /api/auth/addresses/<id>/` - Get specific address
- `PUT /api/auth/addresses/<id>/` - Update address
- `DELETE /api/auth/addresses/<id>/` - Delete address
- `POST /api/auth/addresses/<id>/set-default/` - Set as default address

**Phone Verification**:
- `POST /api/auth/phone/send-otp/` - Send OTP to phone
- `POST /api/auth/phone/verify-otp/` - Verify phone with OTP
- `PUT /api/auth/phone/update/` - Update phone number

**Two-Factor Authentication**:
- `POST /api/auth/2fa/setup/` - Initialize 2FA (returns QR code)
- `POST /api/auth/2fa/enable/` - Enable 2FA (verify with code)
- `POST /api/auth/2fa/disable/` - Disable 2FA
- `POST /api/auth/2fa/verify/` - Verify 2FA code during login
- `GET /api/auth/2fa/backup-codes/` - Get backup codes
- `POST /api/auth/2fa/regenerate-backup-codes/` - Generate new backup codes

**Session Management**:
- `GET /api/auth/sessions/` - List all active sessions
- `GET /api/auth/sessions/current/` - Get current session info
- `DELETE /api/auth/sessions/<id>/` - Terminate specific session
- `DELETE /api/auth/sessions/terminate-all/` - Terminate all other sessions

**Security & Audit**:
- `GET /api/auth/login-history/` - View login history
- `GET /api/auth/security/activity/` - Recent account activity
- `POST /api/auth/security/report-suspicious/` - Report suspicious activity

**Account Management**:
- `POST /api/auth/account/deactivate/` - Temporarily deactivate account
- `POST /api/auth/account/reactivate/` - Reactivate account
- `DELETE /api/auth/account/delete/` - Permanently delete account (with confirmation)
- `POST /api/auth/account/export-data/` - Request data export (GDPR compliance)

**User Search & Discovery** (for admin/internal use):
- `GET /api/users/` - List users (admin only, with pagination & filters)
- `GET /api/users/<id>/` - Get user details (admin only)
- `PUT /api/users/<id>/` - Update user (admin only)
- `POST /api/users/<id>/suspend/` - Suspend user account (admin only)
- `POST /api/users/<id>/unsuspend/` - Unsuspend user account (admin only)

#### [NEW] [permissions.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/accounts/permissions.py)
Custom permission classes:
- IsOwnerOrAdmin (user can only access their own data)
- IsVerifiedUser (email verified users only)
- IsTwoFactorAuthenticated
- IsActiveUser

#### [NEW] [utils.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/accounts/utils.py)
Utility functions:
- Generate verification token
- Send verification email
- Send password reset email
- Send OTP SMS
- Validate password strength
- Generate QR code for 2FA
- Encrypt/decrypt sensitive data
- Get client IP and location
- Parse user agent for device info

#### [NEW] [signals.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/accounts/signals.py)
Django signals:
- Create UserProfile when User is created
- Send welcome email on registration
- Log login attempts
- Notify user of password changes
- Clean up expired tokens

#### [NEW] [validators.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/accounts/validators.py)
Custom validators:
- Phone number validator
- Password strength validator
- Email domain validator
- Username validator (no special characters)

#### [NEW] [middleware.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/accounts/middleware.py)
Custom middleware:
- Track user sessions
- Update last activity timestamp
- Rate limiting for login attempts
- IP-based access control

---

### Products App

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/products/models.py)

**Category Model**:
- Name, slug, description
- Parent category (for nested categories)
- Image
- Active status

**Product Model**:
- Vendor (ForeignKey, nullable for admin-owned products)
- Name, slug, SKU
- Description (short and detailed)
- Category (ForeignKey)
- Price, compare_at_price (for discounts)
- Stock quantity
- Multiple product images (separate ProductImage model)
- Weight, dimensions
- Active status
- Featured flag
- Approval status (for vendor products)
- Created and updated timestamps

**ProductImage Model**:
- Product (ForeignKey)
- Image file
- Alt text
- Display order

**ProductVariant Model** (optional, for size/color variations):
- Product (ForeignKey)
- Variant type (size, color, etc.)
- Variant value
- Price adjustment
- Stock quantity

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/products/serializers.py)
- Category serializer (with nested subcategories)
- Product list serializer (minimal fields)
- Product detail serializer (all fields with images)
- Product image serializer
- Product variant serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/products/views.py)
API endpoints:
- `GET /api/products/` - List products (with pagination, filtering, search)
- `GET /api/products/<slug>/` - Product detail
- `GET /api/categories/` - List categories
- `GET /api/categories/<slug>/` - Category detail with products
- `POST /api/products/` - Create product (admin only)
- `PUT /api/products/<id>/` - Update product (admin only)
- `DELETE /api/products/<id>/` - Delete product (admin only)

---

### Cart App

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/cart/models.py)

**Cart Model**:
- User (ForeignKey, nullable for guest carts)
- Session key (for guest users)
- Created and updated timestamps

**CartItem Model**:
- Cart (ForeignKey)
- Product (ForeignKey)
- Variant (ForeignKey, optional)
- Quantity
- Price snapshot (to preserve price at time of adding)

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/cart/serializers.py)
- Cart serializer (with nested items)
- Cart item serializer
- Add to cart serializer
- Update cart item serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/cart/views.py)
API endpoints:
- `GET /api/cart/` - Get current user's cart
- `POST /api/cart/add/` - Add item to cart
- `PUT /api/cart/items/<id>/` - Update cart item quantity
- `DELETE /api/cart/items/<id>/` - Remove item from cart
- `DELETE /api/cart/clear/` - Clear entire cart

---

### Orders App

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/orders/models.py)

**Order Model**:
- Order number (auto-generated unique)
- User (ForeignKey)
- Vendor (ForeignKey, nullable for multi-vendor orders)
- Status (pending, processing, shipped, delivered, cancelled)
- Subtotal, tax, shipping_cost, discount_amount, total
- Coupon (ForeignKey, nullable)
- Shipping address fields
- Billing address fields
- Payment method
- Payment status
- Tracking number
- Notes
- Created and updated timestamps

**OrderItem Model**:
- Order (ForeignKey)
- Product (ForeignKey)
- Variant (ForeignKey, optional)
- Product name snapshot
- Quantity
- Price snapshot
- Subtotal

**ShippingAddress Model**:
- User (ForeignKey)
- Full name
- Phone number
- Address line 1 & 2
- City, state, postal code, country
- Is default flag

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/orders/serializers.py)
- Order list serializer
- Order detail serializer (with items)
- Order item serializer
- Create order serializer
- Shipping address serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/orders/views.py)
API endpoints:
- `GET /api/orders/` - List user's orders
- `GET /api/orders/<order_number>/` - Order detail
- `POST /api/orders/` - Create order from cart
- `PUT /api/orders/<id>/cancel/` - Cancel order
- `GET /api/orders/<id>/invoice/` - Generate invoice (PDF)
- `GET /api/shipping-addresses/` - List saved addresses
- `POST /api/shipping-addresses/` - Add new address
- `PUT /api/shipping-addresses/<id>/` - Update address
- `DELETE /api/shipping-addresses/<id>/` - Delete address

---

### Payments App (Multi-Gateway Support)

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/payments/models.py)

**PaymentGateway Model**:
- Name (Stripe, PayPal, Razorpay, etc.)
- Gateway code (unique identifier)
- Is active flag
- Configuration (JSONField for API keys, settings)
- Supported currencies
- Logo image
- Display order

**Payment Model**:
- Order (OneToOneField)
- Gateway (ForeignKey to PaymentGateway)
- Payment method (card, wallet, upi, etc.)
- Transaction ID
- Gateway transaction ID
- Amount
- Currency
- Status (pending, processing, completed, failed, refunded)
- Payment gateway response (JSONField)
- Failure reason
- Refund amount
- Refund status
- Created timestamp
- Updated timestamp

**PaymentMethod Model** (Saved payment methods):
- User (ForeignKey)
- Gateway (ForeignKey)
- Method type (card, bank_account)
- Last 4 digits
- Card brand (Visa, Mastercard, etc.)
- Expiry month/year
- Is default flag
- Gateway customer ID
- Gateway payment method ID
- Created timestamp

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/payments/serializers.py)
- Payment gateway serializer
- Payment serializer
- Payment method serializer
- Initiate payment serializer
- Refund request serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/payments/views.py)
API endpoints:
- `GET /api/payment-gateways/` - List available payment gateways
- `POST /api/payments/initiate/` - Initiate payment with selected gateway
- `POST /api/payments/stripe/webhook/` - Stripe webhook handler
- `POST /api/payments/paypal/webhook/` - PayPal webhook handler
- `POST /api/payments/razorpay/webhook/` - Razorpay webhook handler
- `GET /api/payments/<id>/status/` - Check payment status
- `POST /api/payments/<id>/refund/` - Request refund
- `GET /api/payment-methods/` - List saved payment methods
- `POST /api/payment-methods/` - Save new payment method
- `DELETE /api/payment-methods/<id>/` - Remove payment method

#### [NEW] [gateways/](file:///home/lucentinnovation/Desktop/My project/exomDjango/payments/gateways/)
Payment gateway integrations:
- `stripe_gateway.py` - Stripe integration
- `paypal_gateway.py` - PayPal integration
- `razorpay_gateway.py` - Razorpay integration
- `base_gateway.py` - Abstract base class for gateways

---

### Vendors App (Multi-Vendor Support)

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/vendors/models.py)

**Vendor Model**:
- User (OneToOneField)
- Business name
- Business type (individual, company)
- Business registration number
- Tax ID
- Description
- Logo
- Banner image
- Commission rate (percentage)
- Status (pending, approved, suspended, rejected)
- Is verified flag
- Rating (average)
- Total sales
- Total products
- Created timestamp
- Approved timestamp

**VendorProfile Model**:
- Vendor (OneToOneField)
- Phone number
- Email
- Website
- Address fields
- Bank account details (encrypted)
- Payment preferences
- Social media links

**VendorDocument Model** (KYC documents):
- Vendor (ForeignKey)
- Document type (ID proof, address proof, business license)
- Document file
- Status (pending, verified, rejected)
- Rejection reason
- Uploaded timestamp
- Verified timestamp

**VendorPayout Model**:
- Vendor (ForeignKey)
- Amount
- Period start/end dates
- Status (pending, processing, completed, failed)
- Payment method
- Transaction reference
- Created timestamp
- Processed timestamp

**VendorReview Model**:
- Vendor (ForeignKey)
- User (ForeignKey)
- Order (ForeignKey)
- Rating (1-5)
- Review text
- Response from vendor
- Created timestamp

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/vendors/serializers.py)
- Vendor registration serializer
- Vendor profile serializer
- Vendor document serializer
- Vendor payout serializer
- Vendor review serializer
- Vendor dashboard stats serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/vendors/views.py)
API endpoints:
- `POST /api/vendors/register/` - Register as vendor
- `GET /api/vendors/profile/` - Get vendor profile
- `PUT /api/vendors/profile/` - Update vendor profile
- `POST /api/vendors/documents/` - Upload KYC documents
- `GET /api/vendors/dashboard/` - Vendor dashboard stats
- `GET /api/vendors/products/` - List vendor's products
- `GET /api/vendors/orders/` - List vendor's orders
- `PUT /api/vendors/orders/<id>/update-status/` - Update order status
- `GET /api/vendors/payouts/` - List payouts
- `GET /api/vendors/analytics/` - Sales analytics
- `GET /api/vendors/<id>/` - Public vendor profile
- `GET /api/vendors/<id>/reviews/` - Vendor reviews
- `POST /api/vendors/<id>/review/` - Add vendor review

**Admin endpoints**:
- `GET /api/admin/vendors/` - List all vendors
- `PUT /api/admin/vendors/<id>/approve/` - Approve vendor
- `PUT /api/admin/vendors/<id>/suspend/` - Suspend vendor
- `POST /api/admin/vendors/payouts/process/` - Process payouts

---

### Reviews App (Product Reviews & Ratings)

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/reviews/models.py)

**ProductReview Model**:
- Product (ForeignKey)
- User (ForeignKey)
- Order (ForeignKey, to verify purchase)
- Rating (1-5)
- Title
- Review text
- Pros (optional)
- Cons (optional)
- Is verified purchase
- Helpful count
- Not helpful count
- Status (pending, approved, rejected)
- Created timestamp
- Updated timestamp

**ReviewImage Model**:
- Review (ForeignKey)
- Image file
- Caption

**ReviewHelpful Model**:
- Review (ForeignKey)
- User (ForeignKey)
- Is helpful (boolean)
- Created timestamp

**ReviewResponse Model** (Vendor/Admin response):
- Review (OneToOneField)
- Responder (ForeignKey to User)
- Response text
- Created timestamp

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/reviews/serializers.py)
- Product review serializer
- Review image serializer
- Review response serializer
- Review summary serializer (rating distribution)

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/reviews/views.py)
API endpoints:
- `GET /api/products/<id>/reviews/` - List product reviews
- `POST /api/products/<id>/reviews/` - Add review (requires purchase)
- `GET /api/reviews/<id>/` - Get review detail
- `PUT /api/reviews/<id>/` - Update own review
- `DELETE /api/reviews/<id>/` - Delete own review
- `POST /api/reviews/<id>/helpful/` - Mark review as helpful
- `POST /api/reviews/<id>/respond/` - Vendor/admin response
- `GET /api/reviews/my-reviews/` - User's reviews
- `GET /api/products/<id>/review-summary/` - Rating distribution

---

### Wishlist App

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/wishlist/models.py)

**Wishlist Model**:
- User (OneToOneField)
- Created timestamp
- Updated timestamp

**WishlistItem Model**:
- Wishlist (ForeignKey)
- Product (ForeignKey)
- Variant (ForeignKey, optional)
- Added timestamp
- Price snapshot (to track price changes)
- Notify on price drop
- Notify on back in stock

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/wishlist/serializers.py)
- Wishlist serializer
- Wishlist item serializer
- Add to wishlist serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/wishlist/views.py)
API endpoints:
- `GET /api/wishlist/` - Get user's wishlist
- `POST /api/wishlist/add/` - Add item to wishlist
- `DELETE /api/wishlist/items/<id>/` - Remove from wishlist
- `POST /api/wishlist/items/<id>/move-to-cart/` - Move to cart
- `DELETE /api/wishlist/clear/` - Clear wishlist
- `GET /api/wishlist/check/<product_id>/` - Check if product in wishlist

---

### Coupons App (Discount System)

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/coupons/models.py)

**Coupon Model**:
- Code (unique)
- Description
- Discount type (percentage, fixed_amount, free_shipping)
- Discount value
- Minimum order amount
- Maximum discount amount
- Usage limit (total)
- Usage per user limit
- Valid from
- Valid until
- Is active
- Applicable to (all, specific categories, specific products)
- Categories (ManyToMany, optional)
- Products (ManyToMany, optional)
- Exclude sale items
- Created timestamp

**CouponUsage Model**:
- Coupon (ForeignKey)
- User (ForeignKey)
- Order (ForeignKey)
- Discount amount
- Used timestamp

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/coupons/serializers.py)
- Coupon serializer
- Coupon validation serializer
- Apply coupon serializer
- Coupon usage serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/coupons/views.py)
API endpoints:
- `POST /api/coupons/validate/` - Validate coupon code
- `POST /api/coupons/apply/` - Apply coupon to cart
- `DELETE /api/coupons/remove/` - Remove applied coupon
- `GET /api/coupons/available/` - List available coupons for user
- `GET /api/coupons/my-coupons/` - User's available coupons

**Admin endpoints**:
- `GET /api/admin/coupons/` - List all coupons
- `POST /api/admin/coupons/` - Create coupon
- `PUT /api/admin/coupons/<id>/` - Update coupon
- `DELETE /api/admin/coupons/<id>/` - Delete coupon
- `GET /api/admin/coupons/<id>/usage/` - Coupon usage statistics

---

### Inventory App

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/inventory/models.py)

**Warehouse Model**:
- Name
- Code (unique)
- Address fields
- Manager (ForeignKey to User)
- Is active
- Created timestamp

**Stock Model**:
- Product (ForeignKey)
- Variant (ForeignKey, optional)
- Warehouse (ForeignKey)
- Quantity
- Reserved quantity (for pending orders)
- Available quantity (calculated)
- Reorder level
- Reorder quantity
- Updated timestamp

**StockMovement Model** (Audit trail):
- Product (ForeignKey)
- Variant (ForeignKey, optional)
- Warehouse (ForeignKey)
- Movement type (purchase, sale, return, adjustment, transfer)
- Quantity (positive for in, negative for out)
- Reference type (order, purchase_order, adjustment)
- Reference ID
- Notes
- Created by (ForeignKey to User)
- Created timestamp

**StockAlert Model**:
- Product (ForeignKey)
- Variant (ForeignKey, optional)
- Warehouse (ForeignKey)
- Alert type (low_stock, out_of_stock, overstock)
- Threshold quantity
- Current quantity
- Is resolved
- Created timestamp
- Resolved timestamp

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/inventory/serializers.py)
- Warehouse serializer
- Stock serializer
- Stock movement serializer
- Stock alert serializer
- Stock adjustment serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/inventory/views.py)
API endpoints (Admin/Vendor only):
- `GET /api/inventory/warehouses/` - List warehouses
- `POST /api/inventory/warehouses/` - Create warehouse
- `GET /api/inventory/stock/` - List stock levels
- `GET /api/inventory/stock/<product_id>/` - Get product stock
- `POST /api/inventory/stock/adjust/` - Adjust stock
- `POST /api/inventory/stock/transfer/` - Transfer between warehouses
- `GET /api/inventory/movements/` - Stock movement history
- `GET /api/inventory/alerts/` - Stock alerts
- `PUT /api/inventory/alerts/<id>/resolve/` - Resolve alert
- `GET /api/inventory/reports/low-stock/` - Low stock report

---

### Notifications App (Email Notifications)

#### [NEW] [models.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/notifications/models.py)

**EmailTemplate Model**:
- Name
- Template type (order_confirmation, shipping_update, etc.)
- Subject
- HTML content
- Text content (plain text fallback)
- Variables (JSONField - list of available variables)
- Is active
- Created timestamp
- Updated timestamp

**EmailLog Model**:
- User (ForeignKey, nullable)
- Email address
- Template (ForeignKey)
- Subject
- Status (pending, sent, failed, bounced)
- Error message
- Sent timestamp
- Opened timestamp
- Clicked timestamp

**NotificationPreference Model**:
- User (OneToOneField)
- Order confirmation (boolean)
- Shipping updates (boolean)
- Promotional emails (boolean)
- Newsletter (boolean)
- Product recommendations (boolean)
- Price drop alerts (boolean)
- Back in stock alerts (boolean)

#### [NEW] [serializers.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/notifications/serializers.py)
- Email template serializer
- Email log serializer
- Notification preference serializer

#### [NEW] [views.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/notifications/views.py)
API endpoints:
- `GET /api/notifications/preferences/` - Get notification preferences
- `PUT /api/notifications/preferences/` - Update preferences
- `GET /api/notifications/history/` - Email history

**Admin endpoints**:
- `GET /api/admin/email-templates/` - List templates
- `POST /api/admin/email-templates/` - Create template
- `PUT /api/admin/email-templates/<id>/` - Update template
- `POST /api/admin/email-templates/<id>/test/` - Send test email
- `GET /api/admin/email-logs/` - Email logs

#### [NEW] [tasks.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/notifications/tasks.py)
Celery tasks for async email sending:
- `send_order_confirmation_email(order_id)`
- `send_shipping_update_email(order_id)`
- `send_order_delivered_email(order_id)`
- `send_password_reset_email(user_id, token)`
- `send_welcome_email(user_id)`
- `send_price_drop_alert(user_id, product_id)`
- `send_back_in_stock_alert(user_id, product_id)`

#### [NEW] [utils.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/notifications/utils.py)
Email utility functions:
- Render email template with context
- Send email via SMTP
- Track email opens/clicks
- Handle email bounces

---

### Additional Configuration Files

#### [NEW] [requirements.txt](file:///home/lucentinnovation/Desktop/My project/exomDjango/requirements.txt)
Dependencies:
- Django>=5.0
- djangorestframework
- djangorestframework-simplejwt
- mysqlclient
- django-cors-headers
- Pillow (for image handling)
- python-decouple (for environment variables)
- django-filter (for API filtering)
- celery (for async tasks)
- redis (for Celery broker and caching)
- stripe (Stripe payment gateway)
- paypalrestsdk (PayPal integration)
- razorpay (Razorpay integration)
- qrcode (for 2FA QR codes)
- pyotp (for 2FA)
- cryptography (for encryption)
- django-storages (for cloud storage)
- boto3 (for AWS S3)
- reportlab (for PDF generation)
- django-celery-beat (for scheduled tasks)
- django-celery-results (for task result storage)

#### [NEW] [.env.example](file:///home/lucentinnovation/Desktop/My project/exomDjango/.env.example)
Environment variables template:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated allowed hosts
- `DB_NAME` - MySQL database name
- `DB_USER` - MySQL username
- `DB_PASSWORD` - MySQL password
- `DB_HOST` - MySQL host
- `DB_PORT` - MySQL port
- `STRIPE_PUBLIC_KEY` - Stripe publishable key
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `PAYPAL_CLIENT_ID` - PayPal client ID
- `PAYPAL_SECRET` - PayPal secret
- `PAYPAL_MODE` - PayPal mode (sandbox/live)
- `RAZORPAY_KEY_ID` - Razorpay key ID
- `RAZORPAY_KEY_SECRET` - Razorpay key secret
- `EMAIL_HOST` - SMTP host
- `EMAIL_PORT` - SMTP port
- `EMAIL_HOST_USER` - SMTP username
- `EMAIL_HOST_PASSWORD` - SMTP password
- `EMAIL_USE_TLS` - Use TLS (True/False)
- `REDIS_URL` - Redis connection URL
- `CELERY_BROKER_URL` - Celery broker URL
- `AWS_ACCESS_KEY_ID` - AWS access key (for S3)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_STORAGE_BUCKET_NAME` - S3 bucket name
- `FRONTEND_URL` - Frontend application URL

#### [NEW] [.gitignore](file:///home/lucentinnovation/Desktop/My project/exomDjango/.gitignore)
Ignore sensitive and generated files

#### [NEW] [README.md](file:///home/lucentinnovation/Desktop/My project/exomDjango/README.md)
Project documentation:
- Setup instructions
- API documentation overview
- Database setup guide
- Running the project

---

### Admin Panel Customization

#### [NEW] [admin.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/products/admin.py)
Enhanced admin interface for products with:
- Inline image management
- Bulk actions
- Filters and search

#### [NEW] [admin.py](file:///home/lucentinnovation/Desktop/My project/exomDjango/orders/admin.py)
Order management interface with:
- Order status updates
- Order item inline display
- Export functionality

## Verification Plan

### Automated Tests

Since this is a new project, I will create comprehensive test suites:

#### Unit Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test products
python manage.py test cart
python manage.py test orders
```

**Test files to create**:
- `accounts/tests.py` - Test user registration, login, JWT tokens, profile updates
- `products/tests.py` - Test product CRUD, category operations, filtering
- `cart/tests.py` - Test add/remove items, quantity updates, cart calculations
- `orders/tests.py` - Test order creation, status updates, address management

#### API Integration Tests
```bash
# Test API endpoints with coverage
coverage run --source='.' manage.py test
coverage report
```

### Manual Verification

#### 1. Database Setup Verification
```bash
# Create database
mysql -u root -p
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Verify all tables created
python manage.py dbshell
SHOW TABLES;
```

#### 2. Admin Panel Verification
```bash
# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access admin panel at http://localhost:8000/admin/
# Verify you can:
# - Create categories
# - Create products with images
# - View orders
# - Manage users
```

#### 3. API Endpoint Testing
Use Postman or curl to test:

**Authentication Flow**:
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

**Product Operations**:
```bash
# List products
curl http://localhost:8000/api/products/

# Get product detail
curl http://localhost:8000/api/products/<product-slug>/
```

**Cart Operations**:
```bash
# Add to cart (requires authentication token)
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'

# View cart
curl http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer <access_token>"
```

**Order Creation**:
```bash
# Create order from cart
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address_id":1,"payment_method":"card"}'
```

#### 4. Database Relationship Verification
```bash
# Access Django shell
python manage.py shell

# Test relationships
from products.models import Product, Category
from orders.models import Order, OrderItem
from accounts.models import User

# Verify foreign key relationships work correctly
# Verify cascade deletes are configured properly
# Check that queries are optimized (no N+1 queries)
```

### Performance Testing
```bash
# Check for missing indexes
python manage.py check --deploy

# Analyze query performance
# Enable Django Debug Toolbar for development
```
