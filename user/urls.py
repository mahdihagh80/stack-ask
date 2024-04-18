from django.urls import path, include
from .views import UserView, LogoutView
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', UserView.as_view()),
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
]

