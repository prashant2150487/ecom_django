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
    