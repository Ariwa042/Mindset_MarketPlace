# Generated by Django 5.1.3 on 2025-03-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0003_alter_otp_options_remove_otp_user_otp_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(blank=True, max_length=32, null=True, unique=True),
        ),
    ]
