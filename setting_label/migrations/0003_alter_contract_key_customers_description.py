# Generated by Django 4.0.1 on 2022-02-02 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting_label', '0002_alter_contract_key_customers_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract_key_customers',
            name='description',
            field=models.TextField(blank=True, default=None, verbose_name='Описание'),
        ),
    ]