from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from functools import wraps


def token_required(view_func):
    """ Аутентификация пользователя с помощью JWT токена """
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        jwt_authenticator = JWTAuthentication()
        try:
            # print(request.headers)  # Печать всех заголовков запроса

            # Попытка извлечь токен из заголовка Authorization
            auth_header = request.headers.get('Authorization')
            # print(f'Authorization Header: {auth_header}')  # Печать заголовка Authorization

            if not auth_header:
                # Попытка извлечь токен из куки
                auth_header = f"Bearer {request.COOKIES.get('access_token')}"
            #     print(f'Authorization from Cookie: {auth_header}')

            # Аутентификация пользователя с помощью JWT токена
            request.META['HTTP_AUTHORIZATION'] = auth_header
            authentication_result = jwt_authenticator.authenticate(request)
            if authentication_result is None:
                raise AuthenticationFailed()
            user, token = authentication_result
            request.user = user
        except AuthenticationFailed:
            return JsonResponse({'detail': 'Authorization required'}, status=401)
        return view_func(self, request, *args, **kwargs)

    return _wrapped_view

