# Generated by Django 5.1.5 on 2025-02-15 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0007_alter_blacklist_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userimageinfo',
            name='background',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userimageinfo',
            name='image_data',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
