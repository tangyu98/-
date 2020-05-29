"""tiantianshengxian URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.urls.converters import register_converter

from django.conf.urls import url, include

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^$', views.index),
    path('index', views.index),
    path('reg', views.register),
    path('reg_v', views.reg_v),
    path('cars',views.cars),
    path('delete/<pk>',views.delete),
    path('cars', views.cars),
    # path('choose',views.choose),
    path('chooseone/<status>/<page>',views.chooseone),
    path('cars_add',views.cars_add),
    path('add_cart/<pk>/<int:num>', views.add_cart),
    path('to_site/<pk>', views.to_site),
    path('find_goods',views.find_goods),
    path('user_center_info', views.user_center_info),
    url('orders/(?P<page>\d+)', views.orders),
    # path('user_center_site', views.user_center_site),
    path('detail/<int:pk>', views.detail),
    path('orders',views.orders),
    path('order',views.order),
    path('log', views.login),
    path('site',views.site),
    path('logout', views.logout),
    url('^third/',include("third.urls")),
    # path('to_order/<int:good_id>', views.to_order),
    path('to_order/<int:way>/<int:good_id>/<order_id>', views.to_order),


    # path('session_num', views.session_num),

    path('to_place/<int:gid>/<int:num>', views.to_place),
    # path('to_place', views.to_place)

    path('changenum', views.changenum),
    path('changestatus', views.changestatus),
    path('changestatusone', views.changestatusone),
    path('<path:path>', views.path),


]
