# Generated by Django 4.0.1 on 2022-02-09 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting_label', '0005_alter_managers_for_sms_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='managers_for_sms',
            name='additionalPhoneNumber',
            field=models.CharField(default=None, max_length=30, verbose_name='Добавочный номер'),
        ),
    ]
