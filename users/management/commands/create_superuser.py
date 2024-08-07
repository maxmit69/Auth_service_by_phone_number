from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'Команда для создания суперпользователя python manage.py create_superuser'

    def handle(self, *args, **options):
        user = User.objects.create_user(
            phone_number='+79000000000',
            first_name='admin',
            last_name='admin',
        )

        user.set_password('admin')
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS('Суперпользователь создан'))
