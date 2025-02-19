from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Announcement, VolunteerResponse
from .serializers import AnnouncementSerializer

class IsCreatorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user or request.user.is_staff

class IsElderlyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.need_help or request.user.is_staff

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrAdmin]

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [permissions.IsAuthenticated, IsElderlyUser]
        elif self.action in ['destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsCreatorOrAdmin]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [permissions.IsAuthenticated, IsCreatorOrAdmin]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.can_help:
            return Announcement.objects.all()
        return Announcement.objects.filter(creator=user)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        announcement = self.get_object()

        # Проверяем, не откликался ли уже этот волонтёр
        if VolunteerResponse.objects.filter(announcement=announcement, volunteer=request.user).exists():
            return Response({"error": "You have already responded to this announcement"}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.can_help:
            response = VolunteerResponse.objects.create(
                announcement=announcement,
                volunteer=request.user
            )
            return Response({"status": "You have responded to the announcement"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "You are not authorized to respond to this announcement"}, status=status.HTTP_403_FORBIDDEN)
