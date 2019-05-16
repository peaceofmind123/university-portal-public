from django.shortcuts import render,redirect,Http404,HttpResponse
from datarepo.models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth import login
from datarepo.decorators import check_permission
import datetime
# Create your views here.


def signup(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST,request.FILES)
        if form.is_valid():
            studentuser = form.save()
            deleting_user = accounts.TempStudentUser.objects.get(rollno=studentuser.rollno)
            studentuser.profiletype = 'StudentUser'
            studentuser.batch = deleting_user.batch
            studentuser.stream = deleting_user.stream
            studentuser.save()
            deleting_user.delete()
            login(request,studentuser)
            print(form.cleaned_data['username'])
            print(form.cleaned_data['first_name'])
            print(form.cleaned_data['rollno'])
            print(form.cleaned_data['email'])
            print(form.cleaned_data['profilepic'])
            return redirect('datarepo:index')
    else:
        form = StudentSignupForm()

    return render(request,'studentapp/signup.html',{'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def editinfo(request):
    if request.method == 'POST':
        form = StudentUpdateForm(request.POST,request.FILES,instance=request.user)
        if form.is_valid():
            studentuser = form.save()
            return redirect('studentapp:profile')
    else:
        form = StudentUpdateForm(instance=request.user)

    return render(request,'studentapp/editinfo.html',{'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def changepassword(request):
    if request.method == 'POST':
        form = StudentPasswordForm(request.user,request.POST)
        if form.is_valid():
            studentuser = form.save()
            return redirect('studentapp:profile')
    else:
        form = StudentPasswordForm(request.user)

    return render(request,'studentapp/changepassword.html',{'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def index(request):
    courses = []
    remaining_assignments = []
    for course in request.user.get_courses():
        if course.classplans.exists():
            remaining_classdates = [classplan.classdate for classplan in course.classplans.all() if
                                    classplan.classdate >= datetime.date.today()]
        else:
            remaining_classdates = []

        assignments = course.get_assignments()
        submitted_assignments = []
        for assignment in assignments:
            for each in request.user.submissions.all():
                if each.assignment.name == assignment.name:
                    submitted_assignments.append(assignment)
        for assignment in assignments:
            if assignment not in submitted_assignments:
                remaining_assignments.append(assignment)

        completed_tests = [test for test in course.get_tests() if test.results.exists()]
        passed_tests = []
        tests = []
        for test in completed_tests:
            marks_obtained = 0  # to account for absences
            for result in test.results.all():
                if (result.student.rollno == request.user.rollno):
                    marks_obtained = result.marks_obtained
                    if (result.marks_obtained >= test.passmarks):
                        passed_tests.append(test)
            testdict = {
                'y': str(test.classplan.classdate),
                'a': marks_obtained
            }
            tests.append(testdict)

        coursedata = {
            'data': course,
            'remaining_classdates': remaining_classdates,
            'submitted_count': len(submitted_assignments),
            'not_submitted_count': len(assignments) - len(submitted_assignments),
            'tests': tests,
            'passed_count': len(passed_tests),
            'failed_count': len(completed_tests) - len(passed_tests)
        }
        courses.append(coursedata)

    return render(request,'studentapp/index.html',{'courses':courses,'remaining_assignments':remaining_assignments})


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def profile(request):
    return render(request,'studentapp/profile.html')


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def courselist(request):
    courses = request.user.get_courses()
    return render(request,'studentapp/courselist.html',{'courses':courses})


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def assignmentlist(request):
    courses = request.user.get_courses()
    assignments = []
    submitted_assignments= []
    for eachcourse in courses:
        for each in eachcourse.get_assignments():
            assignments.append(each)
    for assignment in assignments:
        try:
            request.user.submissions.get(assignment__pk=assignment.pk)
            submitted_assignments.append(assignment)
        except education.Submission.DoesNotExist:
            pass
    deadline_near = [assignment for assignment in assignments if((assignment.submission_deadline-datetime.date.today()).days <=5 and (assignment.submission_deadline-datetime.date.today()).days >=0) and (assignment not in submitted_assignments)]
    assignment_count = len(assignments)
    deadline_crossed_count = len([assignment for assignment in assignments if assignment.submission_deadline < datetime.date.today()])
    deadline_upcoming_count = len([assignment for assignment in assignments if assignment.submission_deadline >= datetime.date.today()])
    context = {
        'courses':courses,
        'assignments':assignments,
        'assignment_count':assignment_count,
        'submitted_assignments':submitted_assignments,
        'deadline_near':deadline_near,
        'deadline_crossed_count':deadline_crossed_count,
        'deadline_upcoming_count':deadline_upcoming_count,
    }
    return render(request,'studentapp/assignmentlist.html',context)


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def handoutlist(request):
    courses = request.user.get_courses()
    handouts = []
    for eachcourse in courses:
        for each in eachcourse.get_handouts():
            handouts.append(each)
    handout_count = len(handouts)
    context = {
        'courses': courses,
        'handouts': handouts,
        'handout_count': handout_count,
    }
    return render(request, 'studentapp/handoutlist.html', context)


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def testlist(request):
    courses = [];
    upcoming_tests = [];
    for course in request.user.get_courses():
        tests = [];
        for test in course.get_tests():
            if test.results.exists():
                try:
                    result = request.user.results.get(test__test_id=test.test_id);
                except education.Result.DoesNotExist:
                    result = 'Absent'
            else:
                result = None
            tests.append({
                'data':test,
                'result':result
            })
            if (test.classplan.classdate-datetime.date.today()).days <= 5 and (test.classplan.classdate-datetime.date.today()).days >= 0:
                upcoming_tests.append(test)
        courses.append({
            'data':course,
            'tests':tests
        })
    return render(request,'studentapp/testlist.html',{'courses':courses,'upcoming_tests':upcoming_tests})


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def noticelist(request):
    notices = education.Notice.objects.all()
    return render(request,'studentapp/noticelist.html',{'notices':notices})

@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def notifications(request):
    notifications = request.user.notifications.all()
    return render(request,'studentapp/notifications.html',{'notifications':notifications})
