from django.contrib.auth.models import BaseUserManager, Group

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, sex, date, can_help=False, need_help=False, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            sex=sex,
            date=date,
            can_help=can_help,
            need_help=need_help,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        
        # Assign user to the appropriate group
        if can_help:
            group, created = Group.objects.get_or_create(name='Volunteers')
            user.groups.add(group)
        elif need_help:
            group, created = Group.objects.get_or_create(name='Elderly')
            user.groups.add(group)
        
        return user

    def create_superuser(self, email, first_name, last_name, phone_number, sex, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('can_help', False)  # Добавлено
        extra_fields.setdefault('need_help', False)  # Добавлено

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, phone_number, sex, password=password, **extra_fields)
