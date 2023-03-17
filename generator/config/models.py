from django.db import models


class CentralMikrotik(models.Model):
    filial = models.CharField(max_length=30, verbose_name="Filial")
    ip_mikrotik = models.GenericIPAddressField()

    def __str__(self):
        return self.filial



