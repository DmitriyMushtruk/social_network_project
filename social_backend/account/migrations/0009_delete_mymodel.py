# Generated by Django 4.2.3 on 2023-08-06 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_remove_user_roles_alter_user_role'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MyModel',
        ),
    ]