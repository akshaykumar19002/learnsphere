# Generated by Django 4.1.9 on 2023-07-03 12:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_message', models.TextField()),
                ('bot_message', models.TextField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='feedback',
            unique_together={('user', 'course_id')},
        ),
    ]
