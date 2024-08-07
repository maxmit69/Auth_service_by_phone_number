from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages

from .decorators import token_required
from .models import User
from django.urls import reverse
from .services import create_verification_code, verify_code_and_create_user, get_referred_users_list, \
    process_invite_code, validate_phone_number
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        phone_number = request.POST.get('phone_number')
        try:
            # Валидация номера телефона
            validate_phone_number(phone_number)

            # Создает пользователя если его нет в базе данных
            user, created = User.objects.get_or_create(phone_number=phone_number)

            # Генерация и сохранение кода подтверждения
            create_verification_code(user)

            messages.success(request, 'Код подтверждения отправлен')
            return redirect('web:verify')

        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'users/register.html')


class VerifyView(View):
    def get(self, request):
        return render(request, 'users/verify.html')

    def post(self, request):
        phone_number: str = request.POST.get('phone_number')
        code: str = request.POST.get('code')

        result = verify_code_and_create_user(phone_number, code)
        if not result[0]:  # result[0] - булево значение успеха
            messages.error(request, result[1])  # result[1] - сообщение
            return redirect('web:verify')

        # Создание JWT токенов
        refresh = RefreshToken.for_user(result[3])  # result[3] - пользователь
        access_token = str(refresh.access_token)

        # Отправление JWT токенов в заголовки ответа
        response = redirect(reverse('web:profile', args=[result[3].id]))
        response.set_cookie('access_token', access_token)
        response.set_cookie('refresh_token', str(refresh))

        messages.success(request, result[1])
        return response


class UserProfileView(View):
    @token_required
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        referred_users = get_referred_users_list(user)
        return render(request, 'users/profile.html', {'user': user, 'referred_users': referred_users})

    @token_required
    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        used_invite_code = request.POST.get('used_invite_code')
        if not used_invite_code:
            messages.error(request, 'Вы не ввели инвайт-код')
            referred_users = get_referred_users_list(user)
            return render(request, 'users/profile.html', {'user': user, 'referred_users': referred_users})

        success = process_invite_code(user, used_invite_code)
        if success:
            messages.success(request, success[1])

        referred_users = get_referred_users_list(user)
        return render(request, 'users/profile.html', {'user': user, 'referred_users': referred_users})
