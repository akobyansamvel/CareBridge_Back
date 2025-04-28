from django.contrib.auth.models import BaseUserManager, Group

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, first_name, last_name, sex, date_of_birth, passport_series, passport_number,
                    passport_issued_by, passport_issue_date, can_help=False, need_help=False, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number field must be set')
        
        # Создаём пользователя
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            sex=sex,
            date_of_birth=date_of_birth,
            passport_series=passport_series,
            passport_number=passport_number,
            passport_issued_by=passport_issued_by,
            passport_issue_date=passport_issue_date,
            can_help=can_help,
            need_help=need_help,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        # Присваиваем группу
        if can_help:
            group, created = Group.objects.get_or_create(name='Volunteers')
            user.groups.add(group)
        elif need_help:
            group, created = Group.objects.get_or_create(name='Elderly')
            user.groups.add(group)
        
        return user

    def create_superuser(self, phone_number, first_name, last_name, sex, password=None, **extra_fields):
        # Устанавливаем необходимые значения для суперпользователя
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('can_help', False)  # Добавлено
        extra_fields.setdefault('need_help', False)  # Добавлено

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, first_name, last_name, sex, password=password, **extra_fields)
