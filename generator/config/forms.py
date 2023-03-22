from django import forms
from .models import *


class CiscoForm(forms.Form):
    mnemokod = forms.CharField(max_length=50, label="Mnemokod")
    vlan = forms.IntegerField(label="Vlan")
    speed = forms.IntegerField(label="Speed(kbps)")
    ipaddress = forms.GenericIPAddressField(label="IP address")


class MobiboxForm(forms.Form):
    cuMikrotikIP = forms.GenericIPAddressField(label="Central mikrotik IP")
    mnemokod = forms.CharField(max_length=50, label="Mnemokod")
    vlan = forms.IntegerField(label="Vlan")
    tunnel_id = forms.IntegerField(label="Tunnel ID")
    eoip = forms.GenericIPAddressField(label="EoIP remote-address")


class CUMikrotikForm(forms.Form):
    cuMikrotikIP = forms.GenericIPAddressField(label="Central mikrotik IP")
    mnemokod = forms.CharField(max_length=50, label="Mnemokod")
    tunnel_id = forms.IntegerField(label="Tunnel ID")
    remote_address = forms.GenericIPAddressField(label="Client's mikrotik IP L2TP")


class GetL2tpForm(forms.Form):
    cuMikrotikIP = forms.GenericIPAddressField(label="Central mikrotik IP")
    # cuMikrotikIP = forms.ChoiceField(label="Central mikrotik IP")
    mnemokod = forms.CharField(max_length=50, label="Mnemokod")


class ChangeMnemocodMobiboxForm(forms.Form):
    mnemokod = forms.CharField(widget=forms.Textarea, label="Change Mnemokod")


class DeleteMobiboxForm(forms.Form):
    mnemokod = forms.CharField(widget=forms.Textarea, label="Delete Mnemokod")




