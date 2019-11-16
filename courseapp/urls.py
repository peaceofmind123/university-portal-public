from django.urls import path
from . import views

app_name = 'courseapp'

urlpatterns = [
    path('<coursecode>/',views.index,name='index'),
    path('<coursecode>/edit',views.editinfo,name='editinfo'),
    path('<coursecode>/ajax/addchapter',views.addchapter,name='ajax_addchapter'),
    path('<coursecode>/syllabus/',views.syllabus,name='syllabus'),
    path('<coursecode>/courseplan/',views.courseplan,name='courseplan'),
    path('<coursecode>/ajax/addclass',views.addclass,name='ajax_addclass'),
    path('<coursecode>/ajax/editclass',views.editclass,name='ajax_editclass'),
    path('<coursecode>/ajax/cancelclass', views.cancelclass, name='ajax_cancelclass'),
    # path('<coursecode>/courseplan/create', views.createcourseplan, name='createcourseplan'),
    path('<coursecode>/assignments/',views.assignment,name='assignment'),
    path('<coursecode>/ajax/addassign', views.addassignment, name='ajax_addassignment'),
    path('<coursecode>/handouts/',views.handout,name='handout'),
    path('<coursecode>/ajax/addhandout', views.addhandout, name='ajax_addhandout'),
    path('<coursecode>/tests/',views.test,name='test'),
    path('<coursecode>/ajax/addtest',views.addtest,name='ajax_addtest'),
    path('<coursecode>/assignments/<assignmentpk>/submissions',views.submission,name='submission'),
    path('<coursecode>/ajax/addsubmission',views.addsubmission,name='ajax_addsubmission'),
    path('<coursecode>/tests/<testpk>/results',views.result,name='result'),
    path('<coursecode>/ajax/<testpk>/addresult',views.addresult,name='ajax_addresult'),
]