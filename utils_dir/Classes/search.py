import datetime

from utils_dir.Classes.Order import Order
from setting_label.services.variables_delay import *
from setting_label.services.variables_minus import *
from setting_label.services.variables_plus import *
from setting_label.services.key_customers import key_customers_array


class Search:
    def __init__(self, order_number, ek5):
        self.now = datetime.datetime.now()
        self.order = Order(order_number, ek5)
        self.status = "Не_опознано"
        self.count = 0
        # self.status_key = "Не ключевой клиент"
        self.declared_value_status = "Не определено"
        self.declared_value = 0
        try:
            if self.order.price["service"][0]["name"] == "страхование":
                self.declared_value = float(self.order.price["service"][0]["param"])
        except IndexError:
            self.declared_value = 0
        except KeyError:
            for x in range(1, 15, 1):
                try:
                    if self.order.price["service"][x]["name"] == "страхование":
                        self.declared_value = float(self.order.price["service"][x]["param"])
                    break
                except:
                    pass

        if self.declared_value >= 50000:
            self.declared_value_status = "Дорогостоящее"
        else:
            self.declared_value_status = None

        try:
            self.contract_number = str(self.order.order_journal["items"][0]["contractNumber"]).lower()
        except:
            self.contract_number = None

        # for key_client in key_customers_array:
        #     if key_client.lower() == self.contract_number:
        #         self.status_key = "Ключевой_клиент"
        #         break

        def check_status(last_state7):
            if self.order.last_state7 == "Вручено" or self.order.last_state7 == 'Не вручено' or self.order.last_state7 == "Принято в оф.-получателе до востребования" \
                    or self.order.last_state7 == "Выдано на доставку" or self.order.last_state7 == "Возвращено в оф.-доставки" or self.order.last_state7 == "Заложен в постамат" \
                    or self.order.last_state7 == "Принято в оф.-доставки" or self.order.last_state7 == "Изъят из постамата клиентом" \
                    or self.order.last_state7 == "Частично вручено" or self.order.last_state7 == "Заложен в постамат":
                if self.order.last_state7 == "Выдано на доставку" and self.now - self.order.last_date_of_listing8 > datetime.timedelta(
                        days=1):
                    return True
                else:
                    return False
            else:
                return True

        def check_create_order1():
            flag = False
            points = points_check_create_order1
            if self.now - self.order.create_order1 > datetime.timedelta(days=variable_check_create_order1):
                self.count += points
                flag = True
            else:
                pass
            return flag

        def check_delay_order3():
            flag = False
            points = points_check_delay_order3
            if int(self.order.delay_order3) > variable_check_delay_order3:
                self.count += points
                flag = True
            else:
                flag = False
            return flag

        def check_plan_tariff_date4():
            flag = False
            points = points_plan_tariff_date4
            if self.now - self.order.plan_tariff_date4 > datetime.timedelta(days=variable_check_plan_tariff_date4):
                self.count += points
                flag = True
            else:
                flag = False
            return flag

        def check_plan_delivery_date5():
            flag = False
            try:
                points = points_plan_delivery_date5
                if self.now - self.order.plan_delivery_date5 > datetime.timedelta(
                        days=variable_check_plan_delivery_date5):
                    self.count += points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_arrays_status():
            flag = False

            count_status = 0
            try:
                for status in self.order.arrays_status:
                    if status != self.order.last_state7:
                        count_status += 1
                if count_status > len(self.order.arrays_status) * percent_array_status / 100 and len(
                        self.order.arrays_status) > length_array_status and check_status(
                    self.order.last_state7) is True:
                    self.count += points_arrays_status
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_last_date_of_listing8():
            flag = False
            try:
                points = points_last_date_of_listing8
                if self.now - self.order.last_date_of_listing8 > datetime.timedelta(
                        days=variable_last_date_of_listing8):
                    self.count += points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_note_listing12():
            flag = False
            try:
                points = points_note_listing12
                if self.order.note_listing12 == "Автоматом из инвентаризации" and (
                        self.order.last_operation10 == "Консолидация" or self.order.last_operation10 == "Расход Коррекция"):
                    self.count += points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_last_plan_date_dispatch13():
            flag = False
            try:
                points = points_last_plan_date_dispatch13
                if self.now - self.order.last_plan_date_dispatch13 > datetime.timedelta(
                        days=variable_check_last_plan_date_dispatch13):
                    self.count += points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_last_fact_date_meeting16():
            flag = False
            try:
                points = points_last_fact_date_meeting16
                if self.now - self.order.last_fact_date_meeting16 > datetime.timedelta(
                        days=variable_check_last_fact_date_meeting16):
                    self.count += points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_arrays_status_and_date_meeting16():
            flag = False
            try:
                points = points_arrays_status_and_date_meeting16
                if len(self.order.arrays_status) == 1 and (
                        self.order.last_operation10 == "Консолидация" or self.order.last_operation10 == "Приход Коррекция") and self.now - self.order.last_fact_date_meeting16 > datetime.timedelta(
                    days=variable_check_last_status_date_meeting16):
                    self.count += points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_correction():
            flag = False
            try:
                points = points_check_correction

                # ниже метод, который принимает на вход массив и возвращает номер последней ячейки, которая не равна Коррекция УК
                def array_note_sort(array):
                    number_x = 0
                    for i in range(-1, -10, -1):
                        if array[i] != "Коррекция УК":
                            number_x = i
                            break
                    return number_x

                # тут создаю пустой массив, в который буду потом запихивать примечания из складской операции(аля перемменная 12 из класса ордер)
                array_note = []
                # вот через цикл и заполняю свой вышесозданный массив
                for i in range(len(self.order.set_info["items"])):
                    array_note.append(self.order.set_info["items"][i]["note"])

                # идет проверка, если в нашем массиве последние две ячейки Коррекция УК, то двигаем дальше
                if array_note[-1] == "Коррекция УК" and array_note[-2] == "Коррекция УК":
                    # тут мы достаем из ордера дату нашей последней операции, где не было примечание Коррекция УК,
                    # с помощью нашего метода array_note_sort, т.к достается строка, преобразовываем ее
                    date_array = self.order.set_info["items"][array_note_sort(array_note)].get("date").split(" ")
                    date = datetime.datetime.strptime(date_array[0], "%Y-%m-%d")
                    if self.now - date > datetime.timedelta(days=variable_check_correction):
                        self.count += points
                        flag = True
                    else:
                        flag = False
                    return flag
                else:
                    return flag
            except:
                return flag

        def check_delay_msk():
            flag = False
            try:
                points = points_delay_msk
                if self.order.last_operation10 == "Консолидация" and self.order.last_document_number17 == "Москва":
                    if self.now - self.order.in_office15 >= datetime.timedelta(
                            days=variable_check_delay_msk):
                        self.count += points
                        flag = True
                    else:
                        flag = False
                else:
                    flag = False
                return flag
            except:
                return flag

        """*****************************"""
        """ДАЛЕЕ МЕТОДЫ НА МИНУС COUNT"""

        def check_moving_recipient_city():
            flag = False
            points = points_moving_recipient_city
            try:
                if self.order.last_state7 in arr_status and self.order.userCityH2 == self.order.receiverCityH1:
                    if self.now - self.order.last_state_data6 < datetime.timedelta(
                            days=variable_check_moving_recipient_city):
                        self.count -= points
                        flag = True
                    else:
                        flag = False
                    return flag
                return flag
            except:
                return flag

        def check_OG():
            flag = False
            points = points_check_OG
            try:
                if self.order.last_state7 in arr_status_check_OG and self.order.location22 == 'МСК-СЦ-ДМД' \
                        and self.order.shelf[:2] == 'OG':

                    self.count -= points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_erevan_bishkek():
            flag = False
            points = points_check_erevan_bishkek
            try:
                if self.order.last_state7 in arr_status_erevan_bichkek and self.order.location22 == 'МСК-СЦ-ДМД' \
                        and self.order.receiverCityH1 in arr_city_check_erevan:
                    self.count -= points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag



        def check_array_status_minus():
            flag = False

            count_status = 0
            try:
                points = points_arrays_status_minus
                for status in self.order.arrays_status:
                    if status == self.order.last_state7:
                        count_status += 1
                if count_status >= len(self.order.arrays_status) * percent_array_status_minus / 100 and len(
                        self.order.arrays_status) > length_array_status_minus and check_status(
                    self.order.last_state7) is True:
                    self.count -= points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_status_one_minus():
            flag = False
            points = points_status_one_minus
            try:
                if check_status(self.order.last_state7) is False and self.order.warehouse_item_count == 1:
                    if self.order.last_state7 == "Выдано на доставку" and self.now - self.order.last_date_of_listing8 > datetime.timedelta(
                            days=1):
                        flag = False
                    else:
                        self.count -= points
                        flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_status_dontRussia_minus():
            flag = False
            points = points_check_status_dontRussia_minus
            try:
                if self.order.last_city_right_of_listing11 == "Москва (Международная сортировка)" or self.order.last_city_right_of_listing11 == "Таможенное оформление (МСК)" \
                        or self.order.last_city_right_of_listing11 == "Таможенный склад ГТ Пулково" or self.order.last_city_right_of_listing11 == "	Вантаа (Таможенный склад)":
                    self.count -= points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_status_dontRussia_office_minus():
            flag = False
            points = points_check_status_dontRussia_office_minus
            try:
                if self.order.last_office_left_of_listing20 == "Москва (Международная сортировка)" or self.order.last_office_left_of_listing20 == "Фиктиный Владивосток" \
                        or self.order.last_office_left_of_listing20 == "Фиктиный Екатеринбург":
                    self.count -= points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_date_last_operation_minus():
            flag = False
            points = points_check_date_last_operation_minus
            try:
                if self.order.last_operation10 != "Приход коррекция" and self.now - self.order.last_date_of_listing8 < datetime.timedelta(
                        days=variable_check_date_last_operation_minus) and self.order.note_listing12 != "Автоматом из инвентаризации":
                    self.count -= points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        def check_satellite_cities_minus():
            flag = False
            points = points_check_satellite_cities
            try:
                for city_one, city_two in satellite_cities_dict.items():
                    if (city_one == self.order.recipient_city21 and city_two == self.order.location22) or (
                            city_one == self.order.location22 and city_two == self.order.recipient_city21):
                        self.count -= points
                        flag = True
                    else:
                        pass
                return flag

            except:
                return flag

        def check_city_change_minus():
            flag = False
            points = points_check_city_change
            status_arr = []
            try:
                for i in range(0, len(self.order.second_order_parameters_set["items"]), 1):
                    status_arr.append(self.order.second_order_parameters_set["items"][i]["status"])

                for i in range(0, len(status_arr), 1):
                    for status in status_list:
                        if status_arr[i] == status:
                            for status_city in status_list_city_change:
                                if status_arr[i + 1] == status_city:
                                    self.count -= points
                                    flag = True
                return flag
            except:
                return flag

        def check_last_state_data6_minus():
            flag = False
            points = points_last_state_data6_minus
            try:
                if self.now - self.order.last_state_data6 < datetime.timedelta(
                        days=variable_last_state_data6_minus):
                    self.count -= points
                    flag = True
                else:
                    flag = False
                return flag
            except:
                return flag

        self.check_create_order1 = check_create_order1()
        self.check_delay_order3 = check_delay_order3()
        self.check_plan_tariff_date4 = check_plan_tariff_date4()
        self.check_plan_delivery_date5 = check_plan_delivery_date5()
        self.check_arrays_status = check_arrays_status()
        self.check_last_date_of_listing8 = check_last_date_of_listing8()
        self.check_note_listing12 = check_note_listing12()
        self.check_last_plan_date_dispatch13 = check_last_plan_date_dispatch13()
        self.check_last_fact_date_meeting16 = check_last_fact_date_meeting16()
        self.check_arrays_status_and_date_meeting16 = check_arrays_status_and_date_meeting16()
        self.check_correction = check_correction()
        self.check_delay_msk = check_delay_msk()

        self.check_array_status_minus = check_array_status_minus()
        self.check_status_one_minus = check_status_one_minus()
        self.check_status_dontRussia_minus = check_status_dontRussia_minus()
        self.check_date_last_operation_minus = check_date_last_operation_minus()
        self.check_status_dontRussia_office_minus = check_status_dontRussia_office_minus()
        self.check_satellite_cities_minus = check_satellite_cities_minus()
        self.check_city_change_minus = check_city_change_minus()
        self.check_last_state_data6_minus = check_last_state_data6_minus()
        # self.check_reasons_for_the_delay_minus = check_reasons_for_the_delay()
        self.check_moving_recipient_city = check_moving_recipient_city()
        self.check_erevan_bishkek = check_erevan_bishkek()
        self.check_OG = check_OG()

        """******************************************"""

        def check_city_east_minus():
            flag = False
            points = points_check_city_east
            try:
                for city in list_city:
                    if city == self.order.recipient_city21:
                        if self.check_arrays_status in False and self.order.last_state7 == "Отправлено в оф.-транзит" or self.order.last_state7 == "Отправлено в оф.-получатель":
                            self.count -= points
                            flag = True
                return flag
            except:
                return flag

        """ДАЛЕЕ МЕТОДЫ НА ДОП. ОЧКИ по просрочке"""

        def check_delay_order3_plus():
            try:
                if check_status(self.order.last_state7) is True:
                    if self.check_delay_order3 is True:
                        points = (int(self.order.delay_order3) - variable_check_delay_order3) * points_large_days
                        if points >= max_points_large_days:
                            points = max_points_large_days
                        info = f"Доп. очки за delay_order3 :{points}"
                        self.count += points
                        return info
                    else:
                        info = f"Доп. очки за delay_order3: {0}"
                        return info
                else:
                    info = f"Доп. очки за delay_order3: {0}"
                    return info
            except:
                print("Ошбика check_delay_order3_plus")

        def check_delay_tariff_date4():
            try:
                if check_status(self.order.last_state7) is True:
                    if self.check_plan_tariff_date4 is True:
                        points_str_array = (str(self.now - self.order.plan_tariff_date4 - datetime.timedelta(
                            days=variable_check_plan_tariff_date4)).split(" "))
                        points = int(points_str_array[0]) * points_delay_tariff_date4
                        if points >= max_delay_tariff_date4:
                            points = max_delay_tariff_date4
                        info = f"Доп. delay_tariff_date4 :{points}"
                        self.count += points
                        return info
                    else:
                        info = f"Доп. очки за delay_tariff_date4: {0}"
                        return info
                else:
                    info = f"Доп. очки за delay_tariff_date4: {0}"
                    return info
            except:
                info = f"Доп. очки за delay_tariff_date4: {0} err"
                return info

        def delay_last_date_of_listing8():
            try:
                if check_status(self.order.last_state7) is True:
                    if self.check_last_date_of_listing8 is True:
                        points_str_array = (str(self.now - self.order.last_date_of_listing8 - datetime.timedelta(
                            days=variable_last_date_of_listing8)).split(" "))
                        points = int(points_str_array[0]) * points_delay_last_date_of_listing8
                        if points >= max_points_delay_last_date_of_listing8:
                            points = max_points_delay_last_date_of_listing8
                        info = f"Доп. очки за delay_last_date_of_listing8 :{points}"
                        self.count += points
                        return info
                    else:
                        info = f"Доп. очки за delay_tariff_date4: {0}"
                        return info
                else:
                    info = f"Доп. очки за delay_last_date_of_listing8: {0}"
                    return info

            except:
                print("Ошбика delay_last_date_of_listing8")

        self.check_city_east_minus = check_city_east_minus()

        self.check_delay_order3_plus = check_delay_order3_plus()
        self.check_delay_tariff_date4 = check_delay_tariff_date4()
        self.delay_last_date_of_listing8 = delay_last_date_of_listing8()

        if self.count >= 100:
            self.status = "Поиск"
        else:
            self.status = "Трейсинг"
        if self.order.warehouse_item_count != 1:
            self.status = "Многоместка"

    def search_info(self):
        print(f"       Накладная :{self.order.order_number}")
        print("***************PLUS***************")
        print(f"check_create_order1 = {self.check_create_order1}")
        print(f"check_delay_order3 = {self.check_delay_order3}")
        print(f"check_plan_tariff_date4 = {self.check_plan_tariff_date4}")
        print(f"check_plan_delivery_date5 = {self.check_plan_delivery_date5}")
        print(f"check_arrays_status = {self.check_arrays_status}")
        print(f"check_last_date_of_listing8 = {self.check_last_date_of_listing8}")
        print(f"check_note_listing12 = {self.check_note_listing12}")
        print(f"check_last_plan_date_dispatch13 = {self.check_last_plan_date_dispatch13}")
        print(f"check_last_fact_date_meeting16 = {self.check_last_fact_date_meeting16}")
        print(f"check_arrays_status_and_date_meeting16 = {self.check_arrays_status_and_date_meeting16}")
        print(f"check_correction = {self.check_correction}")
        print(f"check_delay_msk = {self.check_delay_msk}")
        print("***************MINUS***************")
        print(f"check_array_status_minus = {self.check_array_status_minus}")
        print(f"check_status_one_minus = {self.check_status_one_minus}")
        print(f"check_status_dontRussia_minus = {self.check_status_dontRussia_minus}")
        print(f"check_date_last_operation_minus = {self.check_date_last_operation_minus}")
        print(f"check_status_dontRussia_office_minus = {self.check_status_dontRussia_office_minus}")
        print(f"check_satellite_cities_minus = {self.check_satellite_cities_minus}")
        print(f"check_city_change_minus = {self.check_city_change_minus}")
        print(f"check_city_east_minus = {self.check_city_east_minus}")
        print(f"check_last_state_data6_minus = {self.check_last_state_data6_minus}")
        print(f"check_moving_recipient_city = {self.check_moving_recipient_city}")
        print(f"check_erevan_bishkek = {self.check_erevan_bishkek}")
        print(f"check_OG = {self.check_OG}")
        # print(f"check_reasons_for_the_delay_minus = {self.check_reasons_for_the_delay_minus}")
        print("***************BONUS_DELAY***************")
        print(self.check_delay_order3_plus)
        print(self.check_delay_tariff_date4)
        print(self.delay_last_date_of_listing8)
        print("***************RESULT***************")
        print(f"          count = {self.count}")
        print(f"       status = {self.status}")
        # print(f"       status_key = {self.status_key}")
        print(f"       declared_value_status = {self.declared_value_status}")

        print("______________________________________")
