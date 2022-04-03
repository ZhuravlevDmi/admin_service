import datetime

from django.core.exceptions import ValidationError
from django.db import models
from loguru import logger

from managers.services.functions import check_jira_user, jira_corp_db


class Group(models.Model):
    group = models.CharField(max_length=50, unique=True, verbose_name='Группа')

    def __str__(self):
        return self.group

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['id']


class Path_JQL(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              verbose_name='Группа')
    path_jql = models.TextField(unique=True, default=None, verbose_name='Запрос JQL')

    def __str__(self):
        return f'{self.group.group}'

    class Meta:
        verbose_name = 'Запрос JQL'
        verbose_name_plural = 'Запросы JQL'


class Manager(models.Model):
    full_name = models.CharField(max_length=100, unique=True, verbose_name='ФИО')
    login_jira = models.CharField(max_length=100, unique=True)

    monday = models.BooleanField(default=False, verbose_name='пн', blank=True)
    tuesday = models.BooleanField(default=False, verbose_name='вт', blank=True)
    wednesday = models.BooleanField(default=False, verbose_name='ср', blank=True)
    thursday = models.BooleanField(default=False, verbose_name='чт', blank=True)
    friday = models.BooleanField(default=False, verbose_name='пт', blank=True)
    saturday = models.BooleanField(default=False, verbose_name='сб', blank=True)
    sunday = models.BooleanField(default=False, verbose_name='вс', blank=True)

    start_time = models.TimeField(null=True, verbose_name='Начало работы')
    final_time = models.TimeField(null=True, verbose_name='Конец работы')

    day_limit = models.IntegerField(default=45, verbose_name='Дневной лимит')
    counter = models.IntegerField(default=0, verbose_name='Назначенных задач')
    status = models.BooleanField(default=False, verbose_name='Статус')
    hour_limit = models.IntegerField(default=7, verbose_name='Лимит в час')
    hour_counter = models.IntegerField(default=0, verbose_name='Назначенных за час')
    start_time_online = models.TimeField(null=True, verbose_name='Вошел в линию', default=None)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_set',
                              verbose_name='Группа')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'

        # сортировка по алфавиту
        ordering = ['full_name']

    def clean(self):
        qs = Manager.objects.filter(pk=self.pk, login_jira=self.login_jira)
        if qs.exists() is False:
            if check_jira_user(self.login_jira, jira_corp_db) is False:
                raise ValidationError(f'{self.login_jira} нет в Jira')

    def save(self, *args, **kwargs):
        self.clean()
        if self.status:
            # при смене статуса с offline на online, в столбце start_time_online проставляем настоящее время
            qs = Manager.objects.filter(pk=self.pk, status=False)
            if qs.exists():
                self.start_time_online = datetime.datetime.now().time()
        super().save(*args, **kwargs)


