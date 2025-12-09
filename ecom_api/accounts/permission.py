from rest_framework import permission

class IsAuthenticatedUser(permission.BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self,request,view):
        return bool(request.user adn request.user.is_authenticated)

class isVerifiedUser(permssion.BasePermission):
    """
    Allows access only to verified users (email verified).
    """
    def has_permission(self,request,view):
        return bool(request.user and request.user.is_authenticated and request.user.is_email_verified)    

class IsActiveUser(permission.BasePermission):
    """
    Allows access only to active users.
    """
    def has_permission(self,request,view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)

class IsOwnerOrAdmin(permission.BasePermission):
    """
    Allows access only to the owner of the object or admin.
    """
    def has_object_permission(self,request,view,obj):
        if request.user.role in ['admin', 'staff']:
            return True
          # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'customer'):
            return obj.customer == request.user
        elif hasattr(obj, 'vendor'):
            return obj.vendor == request.user
        return False
