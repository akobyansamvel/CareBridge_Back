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
    middle_name = models.CharField(verbose_name='Отчество', max_length=255, blank=True, null=True)  # Добавил отчество
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=15, unique=True)
    sex = models.CharField(verbose_name="Пол", choices=SEX_CHOICES, max_length=7)
    date_of_birth = models.DateField(verbose_name='Дата рождения')

    passport_series = models.CharField(verbose_name='Серия паспорта', max_length=4,null=True)  # Серия паспорта
    passport_number = models.CharField(verbose_name='Номер паспорта', max_length=6,null=True)  # Номер паспорта
    passport_issued_by = models.CharField(verbose_name='Кем выдан паспорт', max_length=255,null=True)  # Кем выдан паспорт
    passport_issue_date = models.DateField(verbose_name='Дата выдачи паспорта', null=True)  # Дата выдачи паспорта

    is_pensioner = models.BooleanField(verbose_name='Пенсионер', default=False)
    is_volunteer = models.BooleanField(verbose_name="Волонтёр", default=False)
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

    # Логин теперь по номеру телефона, а не email
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'sex', 'date_of_birth']

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class PensionerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pensioner_profile")
    address = models.CharField(verbose_name='Адрес регистрации', max_length=255)
    actual_address = models.CharField(verbose_name='Фактический адрес проживания', max_length=255, blank=True, null=True)
    is_same_address = models.BooleanField(verbose_name='Адреса совпадают', default=False)  # Галочка на совпадение адресов

    def __str__(self):
        return f"Пенсионер {self.user.first_name} {self.user.last_name}"


class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="volunteer_profile")
    experience = models.TextField(verbose_name="Опыт", blank=True, null=True)
    profile_picture = models.ImageField(verbose_name="Фото профиля", upload_to='profile_pictures/', blank=True, null=True)  # Фото профиля

    # Добавленные поля для волонтера
    work_zone = models.CharField(verbose_name="Зона работы", max_length=255,null=True)  # Зона работы волонтера
    company_name = models.CharField(verbose_name="Компания/Организация", max_length=255,null=True)  # Компания, на которую работает волонтер

    def __str__(self):
        return f"Волонтёр {self.user.first_name} {self.user.last_name}"
