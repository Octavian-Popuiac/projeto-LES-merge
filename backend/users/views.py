from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from projects.permissions import IsProjectAdmin

User = get_user_model()

class Me(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class Users(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("username",)


# users/views.py

from .serializers import CustomRegisterSerializer

class UserCreation(generics.CreateAPIView):
    serializer_class = CustomRegisterSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(CustomRegisterSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save(self.request)


class UserDeletion(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def delete(self, request, *args, **kwargs):
        """Deletes a user based on the provided user ID in the URL"""
        user = self.get_object()
        user.delete()
        return Response({"detail": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class BulkUserDeletion(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated & IsAdminUser]

    def delete(self, request, *args, **kwargs):
        """Deletes multiple users based on the provided user IDs in the request body"""
        user_ids = request.data.get("ids", [])

        if not user_ids:
            return Response({"detail": "No user IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(id__in=user_ids)
        if users.exists():
            deleted_count, _ = users.delete()
            return Response({"detail": f"{deleted_count} users deleted successfully."},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "No users found with the provided IDs."}, status=status.HTTP_404_NOT_FOUND)