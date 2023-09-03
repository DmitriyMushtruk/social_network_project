# Generated by Django 4.2.3 on 2023-08-17 20:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0003_remove_dislike_page_remove_like_page_dislike_author_and_more'),
        ('account', '0002_alter_user_managers_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='current_page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='page.page'),
        ),
    ]
