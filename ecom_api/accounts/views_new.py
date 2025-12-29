from rest_framework import generics, parsers, permissions
from .serializers import ProfileAvatarSerializer


class UserAvatarUploadView(generics.UpdateAPIView):
    serializer_class = ProfileAvatarSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_object(self):
        return self.request.user
