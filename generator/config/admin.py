from django.contrib import admin
from .models import *


class CentralMikrotikAdmin(admin.ModelAdmin):
    list_display = ('filial', 'ip_mikrotik', 'color')


admin.site.register(CentralMikrotik, CentralMikrotikAdmin)





