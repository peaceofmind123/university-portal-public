from django.urls import path
from . import views
from django.contrib.auth.views import LoginView,LogoutView

app_name = 'datarepo'

urlpatterns = [
    path('',views.index,name='index'),
    path('login/',LoginView.as_view(template_name='login.html'),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('unauthorized/<profile_type>',views.unauthorized,name='unauthorized'),
]