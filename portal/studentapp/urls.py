from django.urls import path
from . import views
from django.contrib.auth.views import LoginView,LogoutView

app_name = 'studentapp'

urlpatterns = [
    path('',views.index,name='index'),
    path('signup/',views.signup,name='signup'),
    path('profile/',views.profile,name='profile'),
    path('edit/', views.editinfo, name='editinfo'),
    path('password/',views.changepassword,name='changepassword'),
    path('courses/',views.courselist,name='courselist'),
    path('assignments/',views.assignmentlist,name='assignmentlist'),
    path('handouts/',views.handoutlist,name='handoutlist'),
    path('tests/',views.testlist,name='testlist'),
    path('notices/',views.noticelist,name='noticelist'),
    path('notifications/',views.notifications,name='notifications'),
]