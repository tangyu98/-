from django.urls import path
from . import views

urlpatterns = [
    path("callback", views.zfb_callback_login, name="zfb-callback"),
    path('order',views.order),
    path('pay',views.pay)

]
