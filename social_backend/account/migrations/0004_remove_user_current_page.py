# Generated by Django 4.2.3 on 2023-08-22 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_current_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='current_page',
        ),
    ]
