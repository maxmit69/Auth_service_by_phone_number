from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
import random
import string
import uuid


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Это поле обязательно для заполнения')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


def generate_invite_code():
    """
    Генерирует случайную строку из 6 букв и цифр
    для использования в качестве кода приглашения
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class User(AbstractBaseUser):
    """ Модель пользователя
    """
    username = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID пользователя',
                          help_text='Введите идентификатор пользователя')
    phone_number = models.CharField(max_length=15, unique=True, verbose_name='Номер телефона',
                                    help_text='Введите номер телефона')
    invite_code = models.CharField(max_length=6, unique=True, blank=True, null=True,
                                   verbose_name='Свой код приглашения',
                                   help_text='Введите код приглашения')
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='referrals',
                                    verbose_name='Пригласивший',
                                    help_text='Кто пригласил вас')
    used_invite_code = models.CharField(max_length=6, blank=True, null=True,
                                        verbose_name='Код приглашения',
                                        help_text='Введите код приглашения')

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        """ Проверка и сохранение кода приглашения при создании пользователя
        """
        if not self.invite_code:
            self.invite_code = generate_invite_code()
        super().save(*args, **kwargs)

    def get_referred_users(self):
        """ Возвращает QuerySet пользователей, которые ввели инвайт-код текущего пользователя
        """
        return User.objects.filter(referred_by=self)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class VerificationCode(models.Model):
    """ Модель кода подтверждения
    """
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона')
    code = models.CharField(max_length=10, verbose_name='Код подтверждения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    def __str__(self):
        return f"Код подтверждения для {self.phone_number} - {self.code}"

    class Meta:
        verbose_name = 'Код подтверждения'
        verbose_name_plural = 'Коды подтверждения'
