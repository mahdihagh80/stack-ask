from django.urls import path, include
from .views import UserView, LogoutView
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'user'

urlpatterns = [
    path('', UserView.as_view(), name='user'),
    path('login/', obtain_auth_token, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

