from django.contrib import admin

from setting_label.models import Contract_key_customers, Managers_for_SMS


class Manager_Contract_key_customers(admin.ModelAdmin):
    list_display = ('label', 'contracts', 'description')
    empty_value_display = '125'
    search_fields = ("label",)
    list_per_page = 25
    ordering = ('label',)


class Managers_for_SMS_Admin(admin.ModelAdmin):
    list_display = ('full_name', 'additionalPhoneNumber', 'send_sms', 'manager_status')

    def manager_status(self, obj):
        from managers.models import Manager
        return Manager.objects.get(pk=obj.full_name_id).status

    manager_status.short_description = "Статус"
    manager_status.boolean = True


admin.site.register(Contract_key_customers, Manager_Contract_key_customers)
admin.site.register(Managers_for_SMS, Managers_for_SMS_Admin)
