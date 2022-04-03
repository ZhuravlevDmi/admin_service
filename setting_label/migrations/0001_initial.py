# Generated by Django 4.0.1 on 2022-02-02 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contract_key_customers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=50, unique=True, verbose_name='Метка')),
                ('contracts', models.TextField(verbose_name='Договоры')),
            ],
            options={
                'verbose_name': 'Метка',
                'verbose_name_plural': 'Метки',
                'ordering': ['id'],
            },
        ),
    ]
