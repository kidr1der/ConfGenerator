from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('create_config/', views.createconfig, name='create_config'),
    path('create_config/cisco/', views.cisco, name='cisco_form'),
    path('create_config/mobibox/', views.mobibox, name='mobibox_form'),
    path('create_config/cumikrotik/', views.cumikrotik, name='cumikrotik_form'),
    path('create_config/get_l2tp_connect/', views.get_l2tp_connect, name='get_l2tp_form'),
    path('change_config/', views.changeconfig, name='change_config'),
    path('change_config/delete-mobibox/', views.deletemobibox, name='delete_mobibox_form'),
    path('change_config/change-mnemokod/', views.changemnemokod, name='change_mnemokod_form'),


]

