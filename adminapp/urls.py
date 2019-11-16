from django.urls import path
from . import views

app_name = 'adminapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('students/', views.studentlist, name='studentlist'),
    path('students/ajax/add', views.addstudent, name='ajax_addstudent'),  # To add single student in a dropdown-selected batch and stream
    path('students/addbatch/', views.addbatch, name='addbatch'),    # To add a whole batch of students , this adds a new batch
    path('streams/',views.streamlist, name='streamlist'),
    path('streams/add',views.addstream, name='addstream'),
    path('stream/<stream_id>',views.streaminfo, name='streaminfo'),
    path('stream/<stream_id>/edit',views.editstream, name='editstream'),
    path('teachers/',views.teacherlist,name='teacherlist'),
    path('teachers/ajax/add', views.addteacher, name='ajax_addteacher'),
    path('courses/',views.courselist,name='courselist'),
    path('courses/add',views.addcourse,name='addcourse'),
    path('notices/',views.noticelist,name='noticelist'),
    path('notices/ajax/add',views.addnotice,name='ajax_addnotice'),
    path('profiler/',views.profileanalysis,name='profileanalysis')
]
