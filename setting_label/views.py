import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from passwords_dir.passwords import EK5_account, jira_rest_api
from setting_label.services.methods import order_analytics
from utils_dir.Classes.EK5 import EK5
from utils_dir.Classes.Jira import Jira
from loguru import logger
from rest_framework.decorators import api_view

ek5 = EK5(EK5_account['user'], EK5_account['password'])
ek5.get_user_token()
jira = Jira(jira_rest_api['login'], jira_rest_api['password'],
            jira_rest_api['url_api'])


@api_view(['POST'])
@csrf_exempt
def index(request):
    """
    Сюда приходит вебхук от корпа, при создании задачи где project = CC AND issuetype = "Работа с вопросами клиента"
    достаем из задачи номер накладной, по номеру накладной определяем какие метки проставить в поступившей задаче
    :param request:
    :return:
    """
    try:
        info_dict = json.loads(request.body)

        ticket = info_dict['issue_key']
        order_num = info_dict.get('issue_title').replace(' ', '')

        result = order_analytics(ticket, order_num, ek5, jira)

        return JsonResponse(result)
    except Exception as e:
        logger.error(f'{e}')
        return JsonResponse(({'error': e}))
