from django.urls import path,include
from . import views
from rest_framework import routers
urlpatterns=[
    path("",views.index,name="index"),
    path("a",views.data_request,name="Radhe"),
    path("register/",views.registration,name="signup"),
    path("approve/",views.approve_registration,name="signup"),
    path("signup/",views.signup_view,name="signup"),
    path("login/",views.login_view,name="signup"),
    path("home/",views.home_view,name="signup"),
]
