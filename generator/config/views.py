import secrets
import string
import re
import paramiko
import os

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from django.http import HttpResponseNotFound, Http404
from django.shortcuts import render
from .forms import *
from .models import *

load_dotenv()


def index(request):
    return render(request, 'config/index.html', {'title': 'Index'})


def createconfig(request):
    return render(request, 'config/create_config.html', {'title': 'Create Config'})


def changeconfig(request):
    return render(request, 'config/change_config.html', {'title': 'Change Config'})


def about(request):
    return render(request, 'config/about.html', {'title': 'About'})


def ssh_connect(ip_device, l2tp_name):
    commands = [f"ppp secret print detail where name={l2tp_name}"]
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(hostname=ip_device, username=os.getenv('secretUser'), password=os.getenv('secretKey'), look_for_keys=False,
               allow_agent=False)
    for command in commands:
        stdin, stdout, stderr = cl.exec_command(command)
    value = stdout.read().decode('ascii')
    cl.close()
    return value


def parser_l2tp(value):
    pattern = re.compile('password="(?P<passwd>\S+)"')
    password = pattern.search(value)
    return password.groupdict().get("passwd")

# def openconfig(nameconf):
#     with open('config/templates/config/' + nameconf, mode='r') as file:
#         conf = file.read()
#     return conf


def shablon_jinja(name_template, context):
    file_loader = FileSystemLoader('config/templates')
    env = Environment(loader=file_loader)
    tm = env.get_template(name_template)
    config = tm.render(context)
    return config


def random_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(16))
    return password


def parsmnemokod(current_form, name):
    if name == "changemnemokod":
        pattern = re.compile(r"[\S ]*?([A-Za-z0-9-]{3,})[\S ]*?([A-Za-z0-9-]{3,})")
    elif name == "deletemobibox":
        pattern = re.compile(r"\S*[A-Za-z0-9-]")
    value = pattern.findall(current_form)
    new_current_form = {'mnemokod': value}
    return new_current_form


def cisco(request):
    if request.method == 'POST':
        form = CiscoForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data
            config = shablon_jinja("cisco.txt", context)
            context["config"] = config
            context["title"] = "Cisco config"
            return render(request, "config/cisco_config.html", context=context)
    else:
        form = CiscoForm()
    return render(request, "config/forma.html", {"title": "Cisco config", "form": form, "name_form": 'cisco_form'})


def mobibox(request):
    ipaddr_mikrotik = CentralMikrotik.objects.all().order_by('filial')
    if request.method == 'POST':
        form = MobiboxForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data
            config = shablon_jinja("mobibox_config.txt", context)
            context["config"] = config
            context["title"] = "Client's Mobibox config"
            return render(request, "config/mobibox_config.html", context=context)
    else:
        form = MobiboxForm()
    return render(request, "config/forma.html", {"title": "Client's Mobibox config", "form": form,
                                                 "ipaddr_mikrotik": ipaddr_mikrotik, "name_form": 'mobibox_form'})


def cumikrotik(request):
    ipaddr_mikrotik = CentralMikrotik.objects.all().order_by('filial')
    if request.method == 'POST':
        form = CUMikrotikForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data
            password = random_password()
            local_address = ".".join(context["remote_address"].split(".")[0:3])
            context["password"] = password
            context["local_address"] = local_address
            config = shablon_jinja("cumikrotik_config.txt", context)
            context["config"] = config
            context["title"] = "Central Mikrotik config"
            return render(request, "config/cumikrotik_config.html", context=context)
    else:
        form = CUMikrotikForm()
    return render(request, "config/forma.html", {"title": "Central Mikrotik config", "form": form,
                                                 "ipaddr_mikrotik": ipaddr_mikrotik, "name_form": 'cumikrotik_form'})


def get_l2tp_connect(request):
    ipaddr_mikrotik = CentralMikrotik.objects.all().order_by('filial')
    if request.method == 'POST':
        form = GetL2tpForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data
            try:
                connect = ssh_connect(context["cuMikrotikIP"], context["mnemokod"])
            except (TimeoutError, paramiko.ssh_exception.NoValidConnectionsError,
                    paramiko.ssh_exception.AuthenticationException):
                return timeout_error(request, context["cuMikrotikIP"])
            else:
                try:
                    password = parser_l2tp(connect)
                except AttributeError:
                    return client_not_found(request, context["cuMikrotikIP"], context["mnemokod"])
            context["password"] = password
            config = shablon_jinja("get_l2tp_config.txt", context)
            context["config"] = config
            context["title"] = "Get l2tp connect mobibox"

            return render(request, "config/get_l2tp_config.html", context=context)
    else:
        form = GetL2tpForm()
    return render(request, "config/forma.html", {"title": "Get l2tp connect mobibox", "form": form,
                                                 "ipaddr_mikrotik": ipaddr_mikrotik, "name_form": 'get_l2tp_form'})


def changemnemokod(request):
    if request.method == 'POST':
        form = ChangeMnemocodMobiboxForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data
            context = parsmnemokod(context['mnemokod'], name='changemnemokod')
            context["title"] = "Change Mnemokod"
            return render(request, "config/change-mnemokod_config.html", context=context)
    else:
        form = ChangeMnemocodMobiboxForm()
    return render(request, "config/change_config_form.html", {"title": "Change mnemokod Mobibox", "form": form, "name_form": 'change_mnemokod_form'})


def deletemobibox(request):
    if request.method == 'POST':
        form = DeleteMobiboxForm(request.POST)
        if form.is_valid():
            context = form.cleaned_data
            context = parsmnemokod(context['mnemokod'], name="deletemobibox")
            context["title"] = "Delete Mobibox"
            return render(request, "config/delete-mobibox_config.html", context=context)
    else:
        form = DeleteMobiboxForm()
    return render(request, "config/change_config_form.html", {"title": "Delete client Mobibox", "form": form, "name_form": 'delete_mobibox_form'})


def timeout_error(request, ip_mikrotik):
    return render(request, "misc/timeout_error.html", {'ip_mikrotik': ip_mikrotik})


def client_not_found(request, ip_mikrotik, mnemokod):
    return render(request, "misc/client_not_found.html", {'mnemokod': mnemokod, 'ip_mikrotik': ip_mikrotik})


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)