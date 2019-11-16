from django.shortcuts import render,redirect,Http404
from django.contrib.auth.decorators import login_required
from .models import *

# Create your views here
def index(request):
    if request.user.is_authenticated:
        usertype = request.user.profiletype
        if(usertype == 'AdminUser'):
            return redirect('adminapp:index')
        elif(usertype == 'StudentUser'):
            return redirect('studentapp:index')
        elif(usertype == 'TeacherUser'):
            return redirect('teacherapp:index')
    return render(request,'index.html')

def unauthorized(request,profile_type):
    return render(request,'datarepo/unauthorized.html',{'profile_type':profile_type})
