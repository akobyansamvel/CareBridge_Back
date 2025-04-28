from rest_framework import serializers
from authentication.models import User, PensionerProfile, VolunteerProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True},  # Убедимся, что пароль можно только записывать
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)  # Извлекаем пароль из данных
        instance = self.Meta.model(**validated_data)
        instance.is_active = True  # Пользователь будет активирован сразу

        if password is not None:
            instance.set_password(password)  # Хэшируем пароль перед сохранением
        instance.save()  # Сохраняем пользователя

        return instance

class PensionerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PensionerProfile
        fields = '__all__'

    def create(self, validated_data):
        # При необходимости добавим логику для создания профиля пенсионера
        return super().create(validated_data)

class VolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerProfile
        fields = '__all__'

    def create(self, validated_data):
        # При необходимости добавим логику для создания профиля волонтера
        return super().create(validated_data)
