from rest_framework.test import APITestCase
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from users.models import VerificationCode
from unittest.mock import patch
from rest_framework.exceptions import ValidationError
from users.serializers import UserSerializer, RegisterAPIViewSerializer
from django.urls import reverse
from users.services import (
    generate_verification_code,
    send_sms,
    create_verification_code,
    verify_code_and_create_user,
    get_referred_users_list,
    process_invite_code
)

User = get_user_model()


class UserTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79000000000")
        self.verification_code = VerificationCode.objects.create(
            phone_number="+79000000000",
            code="1234",
            created_at=timezone.now(),
        )

    def test_verify_code_and_create_user(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(VerificationCode.objects.count(), 1)
        self.assertEqual(self.user.phone_number, "+79000000000")


class InviteCodeTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(phone_number="+79000000001", invite_code="INVIT0")
        self.referred_user1 = User.objects.create_user(phone_number="+79000000002", referred_by=self.user)
        self.referred_user2 = User.objects.create_user(phone_number="+79000000003", referred_by=self.user)
        self.other_user = User.objects.create_user(phone_number="+79000000004", invite_code="INVIT1")

    def test_get_referred_users_list(self):
        referred_users_list = get_referred_users_list(self.user)
        expected_list = [self.referred_user1.phone_number, self.referred_user2.phone_number]
        self.assertEqual(referred_users_list, expected_list)

    def test_process_invite_code_success(self):
        success, message, http_status = process_invite_code(self.other_user, self.user.invite_code)
        self.assertTrue(success)
        self.assertEqual(message, 'Инвайт-код успешно активирован.')
        self.assertEqual(http_status, status.HTTP_200_OK)
        self.assertEqual(self.other_user.referred_by, self.user)

    def test_process_invite_code_own_invite_code(self):
        success, message, http_status = process_invite_code(self.user, self.user.invite_code)
        self.assertFalse(success)
        self.assertEqual(message, 'Вы не можете использовать свой собственный инвайт-код.')
        self.assertEqual(http_status, status.HTTP_403_FORBIDDEN)

    def test_process_invite_code_already_used(self):
        # Сначала успешно активируем инвайт-код
        success, message, http_status = process_invite_code(self.other_user, self.user.invite_code)
        self.assertTrue(success)
        self.assertEqual(http_status, status.HTTP_200_OK)

        # Попробуем снова активировать инвайт-код для того же пользователя
        success, message, http_status = process_invite_code(self.other_user, self.user.invite_code)
        self.assertFalse(success)
        self.assertEqual(message, 'Вы уже использовали инвайт-код.')
        self.assertEqual(http_status, status.HTTP_403_FORBIDDEN)

    def test_process_invite_code_invalid_code(self):
        success, message, http_status = process_invite_code(self.other_user, "INVALIDCODE")
        self.assertFalse(success)
        self.assertEqual(message, 'Неверный инвайт-код.')
        self.assertEqual(http_status, status.HTTP_400_BAD_REQUEST)


class VerificationCodeTests(APITestCase):

    def test_generate_verification_code(self):
        code = generate_verification_code()
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), 4)

    @patch('users.services.print')
    def test_send_sms(self, mock_print):
        phone_number = "+79000000000"
        code = "1234"
        send_sms(phone_number, code)
        mock_print.assert_called_once_with(f'Отправлено SMS на {phone_number}: Ваш код подтверждения {code}')

    @patch('users.services.generate_verification_code', return_value="1234")
    @patch('users.services.send_sms')
    def test_create_verification_code(self, mock_send_sms, mock_generate_verification_code):
        phone_number = "+79000000000"
        verification_code = create_verification_code(phone_number)
        self.assertEqual(verification_code.code, "1234")
        mock_generate_verification_code.assert_called_once()
        mock_send_sms.assert_called_once_with(phone_number, "1234")

    @patch('users.services.timezone.now', return_value=timezone.now())
    def test_verify_code_and_create_user_success(self, mock_timezone_now):
        phone_number = "+79000000000"
        code = "1234"

        verification_code = VerificationCode.objects.create(phone_number=phone_number, code=code)

        success, message, status_code, user = verify_code_and_create_user(phone_number, code)
        self.assertTrue(success)
        self.assertEqual(message, 'Пользователь активирован')
        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_active)

    def test_verify_code_and_create_user_invalid_code(self):
        phone_number = "+79000000000"
        code = "1234"

        success, message, status_code, user = verify_code_and_create_user(phone_number, code)
        self.assertFalse(success)
        self.assertEqual(message, 'Неверный код подтверждения')
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(user)

    def test_verify_code_and_create_user_expired_code(self):
        phone_number = "+79000000000"
        code = "1234"

        verification_code = VerificationCode.objects.create(phone_number=phone_number, code=code)
        verification_code.created_at = timezone.now() - timezone.timedelta(minutes=2)
        verification_code.save()

        success, message, status_code, user = verify_code_and_create_user(phone_number, code)
        self.assertFalse(success)
        self.assertEqual(message, 'Код подтверждения истек')
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(user)


class UserSerializerTests(APITestCase):
    def setUp(self):
        # Создаем тестовые пользователи
        self.user1 = User.objects.create(phone_number='+1234567890', invite_code='INV123')
        self.user2 = User.objects.create(phone_number='+0987654321', invite_code='INV456', referred_by=self.user1)
        self.user3 = User.objects.create(phone_number='+1122334455', invite_code='INV789', referred_by=self.user1)

        # Инициализируем сериализатор с пользователем
        self.serializer = UserSerializer(instance=self.user1)

    def test_get_referred_users(self):
        # Мокаем функцию get_referred_users_list
        with patch('users.serializers.get_referred_users_list') as mock_get_referred_users_list:
            mock_get_referred_users_list.return_value = [self.user2.phone_number, self.user3.phone_number]
            data = self.serializer.data
            expected_referred_users = [self.user2.phone_number, self.user3.phone_number]
            self.assertEqual(data['referred_users'], expected_referred_users)

    def test_validate_used_invite_code_valid(self):
        # Тестируем валидное значение invite_code
        serializer = UserSerializer()
        value = 'INV123'
        validated_code = serializer.validate_used_invite_code(value)
        self.assertEqual(validated_code, value)

    def test_validate_used_invite_code_invalid_empty(self):
        # Тестируем пустое значение invite_code
        serializer = UserSerializer()
        with self.assertRaises(ValidationError) as cm:
            serializer.validate_used_invite_code('')
        self.assertEqual(str(cm.exception.detail[0]), 'Код приглашения не может быть пустым.')

    def test_validate_used_invite_code_invalid_none(self):
        # Тестируем значение None для invite_code
        serializer = UserSerializer()
        with self.assertRaises(ValidationError) as cm:
            serializer.validate_used_invite_code(None)
        self.assertEqual(str(cm.exception.detail[0]), 'Код приглашения не может быть пустым.')

    def test_update_user_with_valid_invite_code(self):
        # Проверяем обновление пользователя с валидным кодом приглашения
        data = {'used_invite_code': 'INV123'}
        serializer = UserSerializer(instance=self.user2, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.referred_by, self.user1)
        self.assertEqual(updated_user.used_invite_code, 'INV123')

    def test_update_user_with_invalid_invite_code(self):
        # Проверяем обновление пользователя с невалидным кодом приглашения
        data = {'used_invite_code': 'INVALID_CODE'}
        serializer = UserSerializer(instance=self.user2, data=data, partial=True)

        # Ожидаем, что сериализатор не пройдет валидацию
        self.assertFalse(serializer.is_valid())

        # Убедитесь, что поля не изменились
        self.assertEqual(self.user2.referred_by, self.user1)
        self.assertNotEqual(self.user2.used_invite_code, 'INVALID_CODE')

        # Примените изменения только если данные валидны
        if serializer.is_valid():
            updated_user = serializer.save()
            self.assertIsNone(updated_user.referred_by)
            self.assertEqual(updated_user.used_invite_code, 'INVALID_CODE')
        else:
            # Если данные не валидны, убедитесь, что данные пользователя остались прежними
            self.assertEqual(self.user2.referred_by, self.user1)  # Или что оно было None до теста
            self.assertNotEqual(self.user2.used_invite_code, 'INVALID_CODE')


class RegisterAPIViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:api-register')

    def test_successful_registration(self):
        data = {'phone_number': '+79000000000'}

        with patch('users.views.validate_phone_number') as mock_validate_phone_number:
            with patch('users.views.create_verification_code') as mock_create_verification_code:
                mock_validate_phone_number.return_value = None
                mock_create_verification_code.return_value = None

                response = self.client.post(self.url, data, content_type='application/json')

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.json()['message'], 'Код подтверждения отправлен')
                mock_validate_phone_number.assert_called_once_with('+79000000000')
                mock_create_verification_code.assert_called_once_with('+79000000000')

    def test_registration_without_phone_number(self):
        data = {'phone_number': ''}

        response = self.client.post(self.url, data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['phone_number'][0], 'This field may not be blank.')

    def test_registration_with_invalid_phone_number(self):
        data = {'phone_number': '+79000000000'}

        with patch('users.views.validate_phone_number') as mock_validate_phone_number:
            mock_validate_phone_number.side_effect = ValueError('Некорректный номер телефона')

            response = self.client.post(self.url, data, content_type='application/json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json()['message'], 'Некорректный номер телефона')
            mock_validate_phone_number.assert_called_once_with('+79000000000')

    def test_registration_exception(self):
        data = {'phone_number': '+79000000000'}

        with patch('users.views.validate_phone_number') as mock_validate_phone_number:
            with patch('users.views.create_verification_code') as mock_create_verification_code:
                mock_validate_phone_number.return_value = None
                mock_create_verification_code.side_effect = Exception('Ошибка при создании кода')

                response = self.client.post(self.url, data, content_type='application/json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.json()['message'], 'Ошибка при создании кода')
                mock_validate_phone_number.assert_called_once_with('+79000000000')
                mock_create_verification_code.assert_called_once_with('+79000000000')

    def test_registration_with_invalid_data(self):
        data = {'phone_number': 'not_a_phone_number'}

        serializer = RegisterAPIViewSerializer(data=data)
        serializer.is_valid()

        response = self.client.post(self.url, data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), serializer.errors)
