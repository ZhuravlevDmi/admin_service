from django.contrib import admin
from .models import Manager, Group, Path_JQL
from .services.functions import check_day_week


class ManagerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'group', 'monday', 'tuesday', 'wednesday',
                    'thursday', 'friday', 'saturday', 'sunday', 'start_time', 'final_time','day_limit', 'counter',
                    'status', 'hour_limit', 'hour_counter', 'start_time_online')
    list_editable = ('monday', 'tuesday', 'wednesday',
                     'thursday', 'friday', 'saturday', 'sunday')

    empty_value_display = ''

    fields = ('full_name', 'group', 'login_jira', 'day_limit', 'monday', 'tuesday', 'wednesday',
              'thursday', 'friday', 'saturday', 'sunday', 'start_time', 'final_time',
              'hour_limit', 'status', 'counter')

    list_filter = ("group",)
    search_fields = ("full_name",)
    list_per_page = 20


class Manager_Path_JQL(admin.ModelAdmin):
    list_display = ('group', 'path_jql')


admin.site.register(Manager, ManagerAdmin)
admin.site.register(Group)
admin.site.register(Path_JQL, Manager_Path_JQL)
