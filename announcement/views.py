from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Announcement, VolunteerResponse
from .serializers import AnnouncementSerializer


class IsCreatorOrAdmin(permissions.BasePermission):
    """
    Разрешение на редактирование и удаление только для создателя или администратора.
    """
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user or request.user.is_staff


class IsElderlyUser(permissions.BasePermission):
    """
    Разрешение на создание только для пенсионеров (пользователей с need_help=True).
    """
    def has_permission(self, request, view):
        return request.user.need_help or request.user.is_staff


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        """
        Настройка прав доступа в зависимости от действия.
        """
        if self.action in ['create']:
            # Создавать могут только пенсионеры
            self.permission_classes = [permissions.IsAuthenticated, IsElderlyUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактировать и удалять могут только создатель или администратор
            self.permission_classes = [permissions.IsAuthenticated, IsCreatorOrAdmin]
        else:
            # Просматривать могут все аутентифицированные пользователи
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Автоматически назначает создателя объявления.
        """
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        """
        Возвращает queryset в зависимости от роли пользователя.
        """
        user = self.request.user
        if user.can_help:
            # Волонтёры видят все объявления
            return Announcement.objects.all()
        # Пенсионеры видят только свои объявления
        return Announcement.objects.filter(creator=user)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """
        Действие для отклика на объявление.
        """
        announcement = self.get_object()

        # Проверяем, не откликался ли уже этот волонтёр
        if VolunteerResponse.objects.filter(announcement=announcement, volunteer=request.user).exists():
            return Response(
                {"error": "You have already responded to this announcement"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.can_help:
            # Создаем отклик, если пользователь — волонтёр
            VolunteerResponse.objects.create(
                announcement=announcement,
                volunteer=request.user
            )
            return Response(
                {"status": "You have responded to the announcement"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": "You are not authorized to respond to this announcement"},
                status=status.HTTP_403_FORBIDDEN
            )