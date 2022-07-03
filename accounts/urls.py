from django.urls import path
from .views import register, LogInUser
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('login/', LogInUser.as_view(), name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(template_name='accounts/logout.html'), name='logout')
]