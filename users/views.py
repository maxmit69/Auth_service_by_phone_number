from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, VerificationCodeRequestSerializer, RegisterAPIViewSerializer
from .services import create_verification_code, verify_code_and_create_user, validate_phone_number, process_invite_code
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


class RegisterAPIView(APIView):
    http_method_names = ['get', 'post', 'options']
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Возвращает поле ввода номера телефона",
        responses={
            200: openapi.Response(
                description='Пример запроса',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Номер телефона'),
                    },
                    examples={
                        'phone_number': 'Номер телефона',
                    }
                )
            )
        },
    )
    def get(self, request):
        return Response({
            UserSerializer.Meta.model.USERNAME_FIELD: 'Номер телефона',
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Создание и отправка кода подтверждения",
        request_body=RegisterAPIViewSerializer,
        responses={
            200: openapi.Response(
                description='Сообщение об отправке кода подтверждения',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Код подтверждения отправлен'),
                    },
                    examples={
                        'message': 'Код подтверждения отправлен',
                    }
                ),
            ),
            400: openapi.Response(
                description='Ошибка валидации',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Неверный номер телефона'),
                    },
                    examples={
                        'message': 'Неверный номер телефона',
                    }
                )
            )
        }
    )
    def post(self, request):
        serializer = RegisterAPIViewSerializer(data=request.data)
        if serializer.is_valid():
            phone_number: str = serializer.validated_data.get('phone_number')

            if not phone_number:
                return Response({'message': 'Поле номера телефона обязательно для заполнения'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                # Валидация номера телефона
                validate_phone_number(phone_number)

                # Сгенерировать и сохранить код подтверждения
                create_verification_code(phone_number)

                return Response({'message': 'Код подтверждения отправлен'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeAPIView(generics.CreateAPIView):
    serializer_class = VerificationCodeRequestSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Возвращает информацию о пользователе",
        operation_summary="Регистрация или авторизация",
        responses={
            200: openapi.Response(
                description="Пользователь успешно создан",
                schema=UserSerializer,
                examples={
                    "application/json": {
                        "id": "4c064d1d-9ef1-4e38-98b4-e05f8683c3bb",
                        "phone_number": "+1234567890",
                        "invite_code": "ABC123",
                        "referred_by": None,
                        "referred_users": [],
                        "used_invite_code": "XYZ789"
                    }
                }
            ),
            400: openapi.Response(
                description="Ошибка верификации",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT,
                                      properties={
                                          "message": openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description="Неверный код подтверждения "
                                                                                "или время жизни кода истекло")
                                      }),
                examples={
                    "application/json": {
                        "detail": "Неверный код подтверждения или время жизни кода истекло"
                    }
                }
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        phone_number: str = request.data.get('phone_number')
        code: str = request.data.get('code')

        success, message, http_status, user = verify_code_and_create_user(phone_number, code)
        if not success:
            return Response({'message': message}, status=http_status)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Отправка пользователю токенов
        response = Response({
            'refresh': str(refresh),
            'access': access_token,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

        # Отправка токенов в заголовках
        response['Authorization'] = f'Bearer {access_token}'
        response['Refresh-Token'] = str(refresh)

        return response


class UserProfileAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_url_kwarg = 'id'
    lookup_field = 'id'

    # http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="Использование инвайт-кода",
        operation_description="Возвращает информацию о пользователе",
        responses={
            400: openapi.Response(
                description="Неверный инвайт-код",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Неверный инвайт-код или '
                                                                                        'пустая строка'),
                    },
                    examples={
                        'message': 'Неверный инвайт-код или пустая строка',
                    }
                )
            ),
            403: openapi.Response(
                description="Ошибка валидации инвайт-кода",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description='Вы не можете использовать свой инвайт-код или '
                                                              'активировать повторно.'),
                    },
                    examples={
                        'message': 'Вы не можете использовать свой инвайт-код или активировали повторно.',
                    }
                )
            ),
            200: openapi.Response(
                description="Информация о пользователе",
                schema=UserSerializer
            )
        }
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        used_invite_code = request.data.get('used_invite_code')

        if used_invite_code is None or used_invite_code == '':
            return Response({'message': 'Вы не ввели инвайт-код'}, status=status.HTTP_400_BAD_REQUEST)

        success, message, http_status = process_invite_code(instance, used_invite_code)

        if not success:
            return Response({'message': message}, status=http_status)

        return Response(UserSerializer(instance).data, status=status.HTTP_200_OK)
