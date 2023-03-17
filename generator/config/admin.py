from django.contrib import admin
from .models import *


class CentralMikrotikAdmin(admin.ModelAdmin):
    list_display = (id, 'filial', 'ip_mikrotik')


admin.site.register(CentralMikrotik, CentralMikrotikAdmin)





