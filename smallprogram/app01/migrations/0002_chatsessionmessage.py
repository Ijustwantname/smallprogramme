# Generated by Django 5.1.5 on 2025-02-12 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSessionMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.UUIDField()),
                ('message', models.TextField()),
                ('role', models.CharField(max_length=16)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('type_message', models.CharField(default='text', max_length=16)),
            ],
        ),
    ]
