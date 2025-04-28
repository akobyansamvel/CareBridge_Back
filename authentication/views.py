from rest_framework.exceptions import ValidationError, NotFound, AuthenticationFailed, PermissionDenied
from rest_framework.viewsets import ModelViewSet
from authentication.models import User, PensionerProfile, VolunteerProfile
from authentication.serializers import UserSerializer, PensionerSerializer, VolunteerSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['POST'], detail=False, url_path='register')
    def register(self, request):
        # Убираем email, используем телефон для регистрации
        phone_number = request.data.get('phone_number')
        if not phone_number:
            raise ValidationError({'error': 'Номер телефона обязателен.'})
        
        # Создаём пользователя
        user = User(
            phone_number=phone_number,
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            middle_name=request.data.get('middle_name', ''),
            sex=request.data.get('sex'),
            date_of_birth=request.data.get('date_of_birth'),
            passport_series=request.data.get('passport_series'),
            passport_number=request.data.get('passport_number'),
            passport_issued_by=request.data.get('passport_issued_by'),
            passport_issue_date=request.data.get('passport_issue_date'),
            is_active=True
        )
        
        # Создаём пароль для пользователя
        password = request.data.get('password')
        if password:
            user.set_password(password)
        
        user.save()

        # Определяем, кого регистрируем: пенсионер или волонтёр
        if request.data.get("is_pensioner"):
            user.is_pensioner = True
            user.save()
            PensionerProfile.objects.create(
                user=user,
                address=request.data.get("address", "")
            )
        elif request.data.get("is_volunteer"):
            user.is_volunteer = True
            user.save()
            VolunteerProfile.objects.create(
                user=user,
                experience=request.data.get("experience", ""),
                work_zone=request.data.get("work_zone", ""),
                company_name=request.data.get("company_name", "")
            )

        return Response({'message': 'Регистрация успешна'})

    @action(methods=['POST'], detail=False, url_path='login')
    def login(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone_number or not password:
            raise ValidationError({'error': 'Номер телефона и пароль обязательны'})

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise NotFound({'error': 'Пользователь не найден'})

        if not user.check_password(password):
            raise AuthenticationFailed({'error': 'Неверный пароль'})

        if not user.is_active:
            raise AuthenticationFailed({'error': 'Аккаунт не активирован'})

        # Генерация JWT-токенов
        refresh = RefreshToken.for_user(user)
        response = Response()
        response.set_cookie('refresh', str(refresh))
        response.data = {
            'accessToken': str(refresh.access_token),
            'user': {
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_pensioner': user.is_pensioner,
                'is_volunteer': user.is_volunteer,
            }
        }

        return response

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated], url_path='me')
    def get_user(self, request):
        user = request.user
        data = self.serializer_class(user).data

        if user.is_pensioner:
            pensioner_data = PensionerSerializer(user.pensioner_profile).data
            data.update({"profile": pensioner_data})
        elif user.is_volunteer:
            volunteer_data = VolunteerSerializer(user.volunteer_profile).data
            data.update({"profile": volunteer_data})

        return Response(data)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated], url_path='logout')
    def logout(self, request):
        response = Response({'message': 'Вы вышли из системы'})
        response.delete_cookie('refresh')
        return response

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            raise PermissionDenied('У вас нет прав на просмотр этих данных.')
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            raise PermissionDenied('У вас нет прав на изменение этих данных.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            raise PermissionDenied('У вас нет прав на удаление этих данных.')
        return super().destroy(request, *args, **kwargs)
