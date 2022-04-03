# Generated by Django 4.0.1 on 2022-02-09 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting_label', '0004_managers_for_sms'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='managers_for_sms',
            options={'ordering': ['full_name'], 'verbose_name': 'Отправка СМС', 'verbose_name_plural': 'Отправка СМС'},
        ),
        migrations.AddField(
            model_name='managers_for_sms',
            name='additionalPhoneNumber',
            field=models.CharField(blank=True, default=False, max_length=30, verbose_name='Отправка СМС'),
        ),
    ]
