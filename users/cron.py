from django_cron import CronJobBase, Schedule
from django.utils import timezone
from datetime import timedelta
from .models import VerificationCode


class DeleteExpiredVerificationCodesJob(CronJobBase):
    RUN_EVERY_MINS = 1  # Каждые 1 минуту

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'users.delete_expired_verification_codes'  # Код для удаления устаревших кодов подтверждения

    def do(self):
        now = timezone.now()
        expired_codes = VerificationCode.objects.filter(created_at__lt=now - timedelta(seconds=60))
        expired_codes.delete()
