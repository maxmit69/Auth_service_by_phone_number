from rest_framework import serializers
from .models import User, VerificationCode
from .services import get_referred_users_list
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    referred_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'invite_code', 'referred_by', 'referred_users', 'used_invite_code']
        read_only_fields = ['referred_by', 'referred_users', 'phone_number', 'invite_code']

    @staticmethod
    def get_referred_users(obj):
        """ Возвращает список с номерами телефонов, которые ввели инвайт-код текущего пользователя """
        return get_referred_users_list(obj)

    @staticmethod
    def validate_used_invite_code(value):
        """Проверка, что код приглашения не пустой"""
        if value is None or value.strip() == '':
            raise ValidationError('Код приглашения не может быть пустым.')
        return value

    def update(self, instance, validated_data):
        # Извлекаем `used_invite_code` (используемый пригласительный код) из валидированных данных, если он есть
        used_invite_code = validated_data.pop('used_invite_code', None)

        if used_invite_code:
            # Поиск пользователя по `invite_code (коду приглашения)
            referred_by = User.objects.filter(invite_code=used_invite_code).first()

            if referred_by:
                # Обновляем `referred_by` и `used_invite_code` для текущего пользователя
                instance.referred_by = referred_by
                instance.used_invite_code = used_invite_code

        # Обновляем остальные данные для текущего пользователя
        return super().update(instance, validated_data)


class VerificationCodeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = ['phone_number', 'code']


class RegisterAPIViewSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
