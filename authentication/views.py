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
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User(
            email=serializer.validated_data['email'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            phone_number=serializer.validated_data['phone_number'],
            sex=serializer.validated_data['sex'],
            date=serializer.validated_data['date'],
            is_active=True
        )
        user.set_password(serializer.validated_data['password'])
        user.save()

        # Определяем, кого регистрируем
        if request.data.get("is_pensioner"):
            user.is_pensioner = True
            user.save()
            PensionerProfile.objects.create(user=user, address=request.data.get("address", ""))
        elif request.data.get("is_volunteer"):
            user.is_volunteer = True
            user.save()
            VolunteerProfile.objects.create(user=user, experience=request.data.get("experience", ""))

        return Response({'message': 'Регистрация успешна'})

    @action(methods=['POST'], detail=False, url_path='login')
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            raise ValidationError({'error': 'E-mail и пароль обязательны'})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFound({'error': 'Пользователь не найден'})

        if not user.check_password(password):
            raise AuthenticationFailed({'error': 'Неверный пароль'})

        if not user.is_active:
            raise AuthenticationFailed({'error': 'Аккаунт не активирован'})

        refresh = RefreshToken.for_user(user)
        response = Response()
        response.set_cookie('refresh', str(refresh))
        response.data = {
            'accessToken': str(refresh.access_token),
            'user': {
                'email': user.email,
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
