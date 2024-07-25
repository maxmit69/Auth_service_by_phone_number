def generate_verification_code():
    import random
    return str(random.randint(1000, 9999))


def send_sms(phone_number, code):
    # Здесь вы можете интегрировать реальный SMS сервис
    print(f'Отправлено SMS на {phone_number}: Ваш код подтверждения {code}')
