import secrets
import string
import re
import paramiko
import socket
import os
from dotenv import load_dotenv

from django.http import HttpResponseNotFound, Http404
from django.shortcuts import render

from .forms import *

load_dotenv()


def index(request):
    return render(request, 'config/index.html', {'title': 'Index'})


def createconfig(request):
    return render(request, 'config/create_config.html', {'title': 'Create Config'})


def changeconfig(request):
    return render(request, 'config/change_config.html', {'title': 'Change Config'})


def about(request):
    return render(request, 'config/about.html', {'title': 'About'})


# def ssh_send_command(request, ip, username, password, commands):
#     cl = paramiko.SSHClient()
#     cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     try:
#         cl.connect(hostname=ip, username=username, password=password, look_for_keys=False, allow_agent=False)
#     except Exception:
#         raise Exception("НЕ МОГУ ПОДКЛЮЧИТЬСЯ К МИКРОТИКУ!")
#     else:
#         for command in commands:
#             stdin, stdout, stderr = cl.exec_command(command)
#         result = stdout.read().decode('ascii')
#         cl.close()
#         return result
#
#
# def ssh_connect(request, device, l2tp_name):
#     commands = [f"ppp secret print detail where name={l2tp_name}"]
#     result = ssh_send_command(request, device, os.getenv('secretUser'), os.getenv('secretKey'), commands)
#     pattern = re.compile('password="(?P<passwd>\S+)"')
#     password = pattern.search(result)
#     return password.groupdict().get("passwd")


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

# def parsmnemokod_del(current_form):
#     new_current_form = {'mnemokod': current_form['mnemokod'].split()}
#     return new_current_form


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
            current_form = form.cleaned_data
            current_form["title"] = "config Cisco"
            return render(request, "config/cisco_config.html", context=current_form)
    else:
        form = CiscoForm()
    return render(request, "config/forma.html", {"title": "config Cisco", "form": form, "name_form": 'cisco_form'})


def mobibox(request):
    if request.method == 'POST':
        form = MobiboxForm(request.POST)
        if form.is_valid():
            current_form = form.cleaned_data
            current_form["title"] = "config client's Mobibox"
            return render(request, "config/mobibox_config.html", context=current_form)
    else:
        form = MobiboxForm()
    return render(request, "config/forma.html", {"title": "config client's Mobibox", "form": form, "name_form": 'mobibox_form'})


def cumikrotik(request):
    if request.method == 'POST':
        form = CUMikrotikForm(request.POST)
        if form.is_valid():
            current_form = form.cleaned_data
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(16))
            local_address = ".".join(current_form["remote_address"].split(".")[0:3])
            current_form["title"] = "config CU Mikrotik"
            current_form["password"] = password
            current_form["local_address"] = local_address
            return render(request, "config/cumikrotik_config.html", context=current_form)
    else:
        form = CUMikrotikForm()
    return render(request, "config/forma.html", {"title": "config CU Mikrotik", "form": form, "name_form": 'cumikrotik_form'})


def get_l2tp_connect(request):
    if request.method == 'POST':
        form = GetL2tpForm(request.POST)
        if form.is_valid():
            current_form = form.cleaned_data
            try:
                connect = ssh_connect(current_form["cuMikrotikIP"], current_form["mnemokod"])
            except (TimeoutError, paramiko.ssh_exception.NoValidConnectionsError,
                    paramiko.ssh_exception.AuthenticationException):
                print("ШЕФ, ВСЕ ПРОПАЛО! КОННЕКТА НЕТ")
                print("ШЕФ, ВСЕ ПРОПАЛО! КОННЕКТА НЕТ")
                print("ШЕФ, ВСЕ ПРОПАЛО! КОННЕКТА НЕТ")
                return timeout_error(request, current_form["cuMikrotikIP"])
            else:
                try:
                    password = parser_l2tp(connect)
                except AttributeError:
                    print("ФСЁЁЁ, КИНА НЕ БУДЕТ. КЛИЕНТА НЕТ")
                    print("ФСЁЁЁ, КИНА НЕ БУДЕТ. КЛИЕНТА НЕТ")
                    print("ФСЁЁЁ, КИНА НЕ БУДЕТ. КЛИЕНТА НЕТ")
                    return client_not_found(request, current_form["cuMikrotikIP"], current_form["mnemokod"])

            current_form["password"] = password
            current_form["title"] = "get l2tp connect mobibox"
            return render(request, "config/get_l2tp_config.html", context=current_form)
    else:
        form = GetL2tpForm()
    return render(request, "config/forma.html", {"title": "get l2tp connect mobibox", "form": form, "name_form": 'get_l2tp_form'})


def changemnemokod(request):
    if request.method == 'POST':
        form = ChangeMnemocodMobiboxForm(request.POST)
        if form.is_valid():
            current_form = form.cleaned_data
            current_form = parsmnemokod(current_form['mnemokod'], name='changemnemokod')
            current_form["title"] = "change Mnemokod"
            return render(request, "config/change-mnemokod_config.html", context=current_form)
    else:
        form = ChangeMnemocodMobiboxForm()
    return render(request, "config/change_config_form.html", {"title": "change mnemokod Mobibox", "form": form, "name_form": 'change_mnemokod_form'})


def deletemobibox(request):
    if request.method == 'POST':
        form = DeleteMobiboxForm(request.POST)
        if form.is_valid():
            current_form = form.cleaned_data
            current_form = parsmnemokod(current_form['mnemokod'], name="deletemobibox")
            current_form["title"] = "delete Mobibox"
            return render(request, "config/delete-mobibox_config.html", context=current_form)
    else:
        form = DeleteMobiboxForm()
    return render(request, "config/change_config_form.html", {"title": "delete client Mobibox", "form": form, "name_form": 'delete_mobibox_form'})


def timeout_error(request, ip_mikrotik):
    print("ВЫЗОВ ФУНКЦИИ timeout_error")
    return render(request, "misc/timeout_error.html", {'ip_mikrotik': ip_mikrotik})


def client_not_found(request, ip_mikrotik, mnemokod):
    print("ВЫЗОВ ФУНКЦИИ client_not_found")
    return render(request, "misc/client_not_found.html", {'mnemokod': mnemokod, 'ip_mikrotik': ip_mikrotik})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)