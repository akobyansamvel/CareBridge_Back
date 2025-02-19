from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    SEX_CHOICES = [
        ("Мужской", "Мужской"),
        ("Женский", "Женский"),
    ]
    
    first_name = models.CharField(verbose_name='Имя', max_length=255)
    last_name = models.CharField(verbose_name='Фамилия', max_length=255)
    email = models.EmailField(verbose_name='Адрес эл. почты', max_length=255, unique=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=15, unique=True)
    sex = models.CharField(verbose_name="Пол", choices=SEX_CHOICES, max_length=7)
    date = models.DateField(verbose_name='Дата рождения')

    is_pensioner = models.BooleanField(verbose_name='Пенсионер', default=False)
    is_volunteer = models.BooleanField(verbose_name='Волонтёр', default=False)

    is_active = models.BooleanField(verbose_name='Активирован', default=True)
    is_staff = models.BooleanField(verbose_name='Модерация', default=False)
    is_superuser = models.BooleanField(verbose_name='Администратор', default=False)

    groups = models.ManyToManyField(
        Group,
        verbose_name="Группы",
        blank=True,
        related_name="custom_user_set"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="Права доступа",
        blank=True,
        related_name="custom_user_permissions_set"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'sex', 'date']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class PensionerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pensioner_profile")
    address = models.CharField(verbose_name='Адрес', max_length=255)

    def __str__(self):
        return f"Пенсионер {self.user.first_name} {self.user.last_name}"


class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="volunteer_profile")
    experience = models.TextField(verbose_name="Опыт", blank=True, null=True)

    def __str__(self):
        return f"Волонтёр {self.user.first_name} {self.user.last_name}"
