# Generated by Django 5.1.4 on 2025-01-25 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account_module', '0006_alter_invitationcode_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='/static/images/logo/easychat-logo.png', upload_to='images/avatars', verbose_name='Avatar'),
        ),
    ]
