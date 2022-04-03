import datetime
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'call_centre_admin_v2.settings')
django.setup()

from django.db.models import F
from loguru import logger
from call_centre_admin_v2.celery import app
from managers.models import Manager, Group, Path_JQL
from managers.services.functions import get_additionalPhoneNumber, jira_corp_db, send_sms_code, validation_phone_number, \
    get_phone_number_client, get_time_create_issue
from passwords_dir.passwords import jira_rest_api, EK5_account
from setting_label.models import Managers_for_SMS
from utils_dir.Classes.EK5 import EK5
from utils_dir.Classes.Jira import Jira


# -----------------------------TASKS-----------------------------
# -----------------------------TASKS-----------------------------
# -----------------------------TASKS-----------------------------
@app.task
def task_on_off_online_status():
    """
    включает пользователей в статус онлайн если время выполнение функции
    попадает в интервал между start_time и final_time
    нужно запускать каждый час в 01 минуту 16,31,46

    так же выключает онлайн тех менеджеров, у кого не рабочий день(условие работает после 4х утра)

    :return:
    """
    qs_tuple_managers = check_manager_work_today()
    now = datetime.datetime.now().time()

    # два времени между котором мы не включаем пользователей в онлайн
    one_time = datetime.time()
    two_time = datetime.time(5, 0)
    flag_time = check_time(one_time, two_time, now)

    for manager_online in qs_tuple_managers[0]:

        if check_time(manager_online.start_time, manager_online.final_time,
                      now) is True and manager_online.status is False and flag_time is False:
            manager_online.status = True
            manager_online.save()
            logger.info(f'Добавили в онлайн {manager_online.full_name} \n'
                        f'{manager_online.start_time}, {manager_online.final_time}, {now}')
            continue
        elif check_time(manager_online.start_time, manager_online.final_time, now) is False and manager_online.status:
            manager_online.status = False
            manager_online.save()
            logger.info(f'Убрали из онлайн {manager_online.full_name}\n'
                        f'{manager_online.start_time}, {manager_online.final_time}, {now}')

    for manager_offline in qs_tuple_managers[1]:
        if manager_offline.status and check_time(manager_offline.start_time, manager_offline.final_time, now) is False:
            manager_offline.status = False
            manager_offline.save()
            logger.info(f'Убрали из онлайн[1] {manager_offline.full_name} \n'
                        f'{manager_offline.start_time}, {manager_offline.final_time}, {now}')
            continue
        elif manager_offline.status and flag_time is False:
            manager_offline.status = False
            manager_offline.save()
            logger.info(f'Убрали из онлайн[2] {manager_offline.full_name} \n'
                        f'{manager_offline.start_time}, {manager_offline.final_time}, {now}')


@app.task
def task_reset_hour_counter():
    """
    сбрасывает на 0 hour_counte
    нужно запускать каждый час
    :return: None
    """
    return Manager.objects.all().update(hour_counter=0)


@app.task
def task_reset_counter():
    """
    сбрасывает на 0 counter
    нужно запускать раз в сутки в интервале от 3х до 8 утра
    :return: None
    """
    return Manager.objects.all().update(counter=0)


@app.task()
def task_assign_ticket():
    """
    Главная таска ответственная за назначение задач на специалиста, в данной функции сначала
    мы получаем все id групп(направлений менеджеров), далее проходимся по ним циклом,
    по каждому направлению мы сначало получаем список специалистов, на которых в данный
    момент времени можно назначить задачу, потом достаем список задач готовых к назначению,
    потом задачи назначаем на специалистов, каждому по одной
    Запускать раз в 3 минуты
    :return:
    """
    jira = Jira(jira_rest_api['login'], jira_rest_api['password'],
                jira_rest_api['url_api'])
    list_group_id = get_group_id()
    logger.info(f'{list_group_id=}')
    for group_id in list_group_id:
        list_managers = get_manager(group_id)
        if list_managers:

            logger.info(f'Менеджеры {Group.objects.get(id=group_id)} - {list_managers}')
            jql = get_jql(group_id)
            dict_info_tickets = jira.get_info_tickets_to_assign(jql, limit=len(list_managers))
            list_tickets_to_assign = get_list_tickets(dict_info_tickets)
            logger.info(f'Задачи для {Group.objects.get(id=group_id)} - {list_tickets_to_assign}')

            if list_tickets_to_assign:
                for index in range(len(list_tickets_to_assign)):
                    # блок назначения задач на менеджеров
                    try:
                        issue = list_tickets_to_assign[index]
                        manager = list_managers[index]
                    except IndexError:
                        logger.critical('Ошибка обращения к списку менеджеров или к списку задач,'
                                        ' они залогированы выше')
                        continue

                    try:
                        logger.debug('Мы в блоке назначения задач')
                        jira.add_transition(issue)
                        jira.assign_issue_api(issue, manager)
                        Manager.objects.filter(login_jira=manager).update(hour_counter=F('hour_counter') + 1)
                        Manager.objects.filter(login_jira=manager).update(counter=F('counter') + 1)

                        logic_send_sms(manager, issue, 'в течение 4 часов')
                    except Exception as e:
                        logger.error(f'Ошибка в блоке назначения задачи на менеджера: {e}')


            else:
                logger.info(f'Не нашлось задач для назначения, группа: {Group.objects.get(id=group_id)}')
                continue
        else:
            logger.info(f' В группе ***{Group.objects.get(id=group_id)}*** нет пользователей онлайн')
            continue


def check_manager_work_today() -> tuple | bool:
    """
    выгружает два qs менеджеров:
     1) которые должны работать в день недели выполнения этой функции
     2) которые не работают в день выполнения функции
    :return: tuple, под индексом 0, менеджеры, которые работают в день выполнения фун-ии
    под индексом 1, менеджеры, которые не работают в день выполнения фун-ии
    """
    today = datetime.datetime.now()
    week_day = today.isoweekday()

    match week_day:
        case 1:
            qs_online = Manager.objects.filter(monday=True)
            qs_offline = Manager.objects.filter(monday=False)
            # qs_yesterday = Manager.objects.filter(sunday=True)
        case 2:
            qs_online = Manager.objects.filter(tuesday=True)
            qs_offline = Manager.objects.filter(tuesday=False)
            # qs_yesterday = Manager.objects.filter(monday=True)
        case 3:
            qs_online = Manager.objects.filter(wednesday=True)
            qs_offline = Manager.objects.filter(wednesday=False)
            # qs_yesterday = Manager.objects.filter(tuesday=True)
        case 4:
            qs_online = Manager.objects.filter(thursday=True)
            qs_offline = Manager.objects.filter(thursday=False)
            # qs_yesterday = Manager.objects.filter(wednesday=True)
        case 5:
            qs_online = Manager.objects.filter(friday=True)
            qs_offline = Manager.objects.filter(friday=False)
            # qs_yesterday = Manager.objects.filter(thursday=True)
        case 6:
            qs_online = Manager.objects.filter(saturday=True)
            qs_offline = Manager.objects.filter(saturday=False)
            # qs_yesterday = Manager.objects.filter(friday=True)
        case 7:
            qs_online = Manager.objects.filter(sunday=True)
            qs_offline = Manager.objects.filter(sunday=False)
            # qs_yesterday = Manager.objects.filter(saturday=True)
        case _:
            return False
    return qs_online, qs_offline


def check_time(start_time: datetime.time, final_time: datetime.time,
               now: datetime.time) -> bool:
    """
    функция проверяет, попадает ли время now в интервал от start_time до final_time
    :param start_time: начало рабочего дня менеджера
    :param final_time: конец рабочего дня менеджера
    :param now: время выполнения функции
    :return: True если now попадает в интервал от start_time до final_time, False если нет
    """

    same_date = start_time <= final_time
    if same_date:
        return start_time <= now <= final_time
    else:
        return now <= final_time or now >= start_time


def get_group_id() -> list:
    """получаем список group_id"""
    return [x[0] for x in Group.objects.values_list('id')]


def get_jql(group_id: int) -> str:
    """
     По group_id достаем jql, по которому можно найти задачи готовые для назначения для группы, которой
     принадлежит group_id, например group_id = 1, это id группы трейсинг
    :param group_id: int, id из таблицы Group
    :return:
    """
    qs_jql = Path_JQL.objects.get(group=group_id)
    return qs_jql.path_jql


def get_manager(group_id: int) -> list:
    """
    Функция возвращает list - список из логинов jira, менеджеров
    на которых можно в данный момент времени назначить задачи, порядок логинов в листе имеет значение,
    от самого приоритетного до менее приоритетных
    От final_time отнимаем час т.к на менеджеров не назначаем задачи в последний час их работы
    :param group_id: Значение из столбца модели Group, например group_id=1 привязана к группе трейсинг
    :return: list - список из логинов jira
    """
    manager_list = []
    now = (datetime.datetime.now()).time()

    qs = Manager.objects.filter(status=True, group_id=group_id, counter__lt=F('day_limit')). \
        exclude(hour_counter__gte=F("hour_limit")).order_by(
        'hour_counter', 'final_time')

    for manager in qs:
        # от конца рабочего дня отнимаем час, т.к. по условию, за час до конца работы, менеджерам нельзя
        # назначать задичи
        if manager.final_time.hour == 0:
            new_final_time = datetime.time(23, manager.final_time.minute)
        else:
            new_final_time = datetime.time(manager.final_time.hour - 1, manager.final_time.minute)

        if check_time(manager.start_time, new_final_time, now):
            manager_list.append(manager.login_jira)

    return manager_list


def get_list_tickets(dict_info_tickets: dict) -> list | bool:
    """
    функция принимает ответ от jql запроса и данная функция этот ответ парсит
    и на выходе получается список из задач готовых к назначению
    :param dict_info_tickets: ответ от функции get_info_tickets_to_assign
    :return: либо лист с задачами, либо false если задач нет
    """
    try:
        return [x['key'] for x in dict_info_tickets['issues']]
    except KeyError:
        logger.info(f'{dict_info_tickets}')
        return False


def logic_send_sms(login_jira: str, issue_num: str, feedback_period: str) -> bool:
    """
    функция принимает все параметры, которые нужны для отправки смс, в ней проверяется можно отправлять или нет смс
    и если все отлично, отправляется смс клиенту
    :param login_jira: жира логин
    :param issue_num: номер задачи
    :param feedback_period: время сколько ждать клиенту, надо добавить в модель
    :return: bool
    """
    ek5 = EK5(EK5_account['user'], EK5_account['password'])
    token = ek5.get_user_token()
    manager = Managers_for_SMS.objects.filter(full_name__login_jira=login_jira).first()
    if manager:
        if manager.send_sms:
            create_time_issue = get_time_create_issue(issue_num.split('-')[1], jira_corp_db).time()
            if check_time(datetime.time(8, 0), datetime.time(0, 0), create_time_issue):
                logger.info('Время подходит')
                additionalPhoneNumber = manager.additionalPhoneNumber
                phone_number = get_phone_number_client(issue_num.split('-')[1], jira_corp_db)
                valid_phone_number = validation_phone_number(phone_number)
                if valid_phone_number:
                    send_sms_code(valid_phone_number, additionalPhoneNumber, issue_num, feedback_period,
                                  manager.full_name.full_name, token)
                    logger.info(f'Отправка СМС на номер {valid_phone_number}')
                    return True
                else:
                    logger.info(f'В задаче {issue_num} не валидный номер {phone_number}')
                    return False
            else:
                logger.info(f'Время {create_time_issue} не подходит для отправки СМС, задача {issue_num}')
                return False
        else:
            logger.info(f'У менеджера - {manager.full_name.full_name}, отключена функция отправки СМС')
            return False
    else:
        logger.info(f'менеджер - {login_jira}, не добавлен в функцию отправки СМС')
        return False
