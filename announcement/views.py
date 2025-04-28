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

        
class IsPensioner(permissions.BasePermission):
    """
    Разрешение на создание только для пенсионеров (пользователей с is_pensioner=True).
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'is_pensioner'):
            print("User does not have attribute 'is_pensioner'")
            return False

        print(f'User is_pensioner: {request.user.is_pensioner}')  # Для отладки
        print(f'User is_staff: {request.user.is_staff}')  # Для отладки
        
        return request.user.is_pensioner or request.user.is_staff




class IsVolunteer(permissions.BasePermission):
    """
    Разрешение на просмотр и отклик только для волонтёров (пользователей с is_volunteer=True).
    """
    def has_permission(self, request, view):
        return request.user.is_volunteer or request.user.is_staff


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        """
        Настройка прав доступа в зависимости от действия.
        """
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, IsPensioner]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsCreatorOrAdmin]
        elif self.action == 'respond':
            self.permission_classes = [permissions.IsAuthenticated, IsVolunteer]
        else:
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
        if user.is_volunteer:
            # Волонтёры видят все объявления
            return Announcement.objects.all()
        # Пенсионеры видят все объявления, созданные ими или другими пенсионерами
        return Announcement.objects.all()

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

        if request.user.is_volunteer:
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
