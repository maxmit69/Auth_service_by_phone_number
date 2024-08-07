import random
from django.utils import timezone
from .models import User, VerificationCode
import phonenumbers
from phonenumbers import NumberParseException
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import status


def generate_verification_code() -> str:
    """ Генерирует случайную строку из 4 цифр """
    return str(random.randint(1000, 9999))


def send_sms(phone_number: str, code: str) -> None:
    # Имитация отправки SMS с кодом подтверждения
    print(f'Отправлено SMS на {phone_number}: Ваш код подтверждения {code}')


def create_verification_code(phone_number: str) -> str:
    """ Генерирует код подтверждения и отправляет его на номер """
    code = VerificationCode.objects.create(phone_number=phone_number, code=generate_verification_code())
    send_sms(phone_number, code.code)
    return code


def verify_code_and_create_user(phone_number: str, code: str) -> tuple[bool, str, int, User | None]:
    """ Проверяет код подтверждения и активирует пользователя """

    try:
        # Проверка на корректность номера телефона
        validate_phone_number(phone_number)

        # Проверка, что номер телефона уже существует в базе данных
        # if not User.objects.filter(phone_number=phone_number).exists():
        #     return False, 'Номер телефона не найден в базе данных', status.HTTP_404_NOT_FOUND

        # Проверка кода верификации
        verification_code = VerificationCode.objects.get(phone_number=phone_number, code=code)

        # Проверка на срок действия кода
        if (timezone.now() - verification_code.created_at).seconds > 60:
            return False, 'Код подтверждения истек', status.HTTP_400_BAD_REQUEST, None

        user, created = User.objects.get_or_create(phone_number=phone_number)
        user.is_active = True
        user.save()

        # Удалить код верификации
        verification_code.delete()
        return True, 'Пользователь активирован', status.HTTP_200_OK, user

    except VerificationCode.DoesNotExist:
        return False, 'Неверный код подтверждения', status.HTTP_400_BAD_REQUEST, None
    except Exception as e:
        return False, str(e), status.HTTP_400_BAD_REQUEST, None


def get_referred_users_list(user):
    """ Возвращает список с номерами телефонов, которые ввели инвайт-код текущего пользователя """
    return [user.phone_number for user in user.get_referred_users()]


def process_invite_code(user: User, invite_code: str) -> bool and str and int:
    """
    Обрабатывает инвайт-код и обновляет пользователя.
    :param user: Пользователь, который вводит инвайт-код
    :param invite_code: Введенный инвайт-код
    :return: Булево значение, сообщение и статус-код
    """
    referred_by = User.objects.filter(invite_code=invite_code).first()
    if referred_by:
        if user.invite_code == invite_code:
            return False, 'Вы не можете использовать свой собственный инвайт-код.', status.HTTP_403_FORBIDDEN
        if user.used_invite_code:
            return False, 'Вы уже использовали инвайт-код.', status.HTTP_403_FORBIDDEN

        user.referred_by = referred_by
        user.used_invite_code = invite_code
        user.save()
        return True, 'Инвайт-код успешно активирован.', status.HTTP_200_OK
    return False, 'Неверный инвайт-код.', status.HTTP_400_BAD_REQUEST


def validate_phone_number(phone_number: str, region=None) -> None:
    """ Проверяем номер телефона на валидность """
    try:
        parsed_number = phonenumbers.parse(phone_number, region)
        if not phonenumbers.is_valid_number(parsed_number):
            raise Exception(f"Неверный номер телефона: {phone_number}")
    except NumberParseException:
        raise Exception(f"Неверный формат номера телефона: {phone_number}")
