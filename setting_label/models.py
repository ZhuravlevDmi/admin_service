from django.core.exceptions import ValidationError
from django.db import models

from managers.models import Manager


class Contract_key_customers(models.Model):
    label = models.CharField(max_length=50, unique=True, verbose_name='Метка')
    contracts = models.TextField(verbose_name='Договоры')
    description = models.TextField(verbose_name='Описание', blank=True, default=None)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Метка'
        verbose_name_plural = 'Метки ключевых клиентов'
        ordering = ['id']

    def clean(self):
        if " " in self.label:
            raise ValidationError(f'Пробелы недопустимы в метках, пробел рекомендуется '
                                  f'заменить на нижнее подчеркивание')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Managers_for_SMS(models.Model):
    full_name = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name='ФИО')
    send_sms = models.BooleanField(default=False, verbose_name='Отправка СМС', blank=True)
    additionalPhoneNumber = models.CharField(max_length=30, default=None, verbose_name='Добавочный номер')

    def __str__(self):
        return self.full_name.full_name

    class Meta:
        verbose_name = 'Отправка СМС'
        verbose_name_plural = 'Отправка СМС'
        ordering = ['full_name']



