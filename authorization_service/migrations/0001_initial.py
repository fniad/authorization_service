# Generated by Django 4.2.3 on 2024-01-30 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=16, unique=True)),
                ('verification_code', models.CharField(max_length=4)),
                ('activated_referral_code', models.CharField(default=None, max_length=8, null=True, unique=True)),
                ('user_referral_code', models.CharField(max_length=8, unique=True)),
                ('user_referred_code_used', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'профиль пользователя',
                'verbose_name_plural': 'профили пользователей',
            },
        ),
    ]
