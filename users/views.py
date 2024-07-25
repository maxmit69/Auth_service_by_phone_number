from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, VerificationCode
from .serializers import UserSerializer, VerificationCodeSerializer
from datetime import timezone


def generate_verification_code():
    import random
    return str(random.randint(1000, 9999))


def send_sms(phone_number, code):
    # Здесь вы можете интегрировать реальный SMS сервис
    print(f'Отправлено SMS на {phone_number}: Ваш код подтверждения {code}')


class RegisterView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        user, created = User.objects.get_or_create(phone_number=phone_number)

        # Сгенерировать и сохранить код подтверждения
        code = VerificationCode.objects.create(user=user, code=generate_verification_code())

        # Имитация отправки SMS
        send_sms(phone_number, code.code)

        return Response({'detail': 'Verification code sent'}, status=status.HTTP_200_OK)


class VerifyView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')

        try:
            user = User.objects.get(phone_number=phone_number)
            verification_code = VerificationCode.objects.get(user=user, code=code)
            if (timezone.now() - verification_code.created_at).seconds > 300:
                return Response({'detail': 'Verification code expired'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()
            verification_code.delete()

            return Response({'detail': 'User verified'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except VerificationCode.DoesNotExist:
            return Response({'detail': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'phone_number'
