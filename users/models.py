from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
import random
import string


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Это поле обязательно для заполнения')
        user = self.model(phone=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


def generate_invite_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=15, unique=True, verbose_name='Номер телефона',
                                    help_text='Введите номер телефона')
    invite_code = models.CharField(max_length=6, unique=True, blank=True, null=True, verbose_name='Код приглашения',
                                   help_text='Введите код приглашения')
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals',
                                    verbose_name='Пригласивший',
                                    help_text='Кто пригласил вас')

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = generate_invite_code()
        super().save(*args, **kwargs)


class VerificationCode(models.Model):
    phone_number = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
