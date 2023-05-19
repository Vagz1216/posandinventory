from django.urls import path
from . import views


#create views here
urlpatterns = [
    path('',views.login_view, name='login_view'),
    path('logout',views.logout_view, name='logout'),
    path('forgot_password',views.forgot_password, name='forgot_password')

]