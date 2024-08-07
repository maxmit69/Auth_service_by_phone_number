# Generated by Django 5.0.7 on 2024-08-03 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_verificationcode_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='used_invite_code',
            field=models.CharField(blank=True, help_text='Введите код приглашения', max_length=6, null=True, verbose_name='Код приглашения'),
        ),
    ]
