from django.shortcuts import render,redirect,Http404,HttpResponse
from datarepo.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import *
from datarepo.decorators import check_permission
import datetime
# Create your views here.


def signup(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST,request.FILES)
        if form.is_valid():
            teacheruser = form.save()
            teacheruser.profiletype = 'TeacherUser'
            teacheruser.save()
            for course in form.cleaned_data['teachable_courses']:   # Looks like manytomany relations can't be saved directly in usercreation forms but in modelforms
                teacheruser.teachable_courses.add(course)
            deleting_user = accounts.TempTeacherUser.objects.get(email=teacheruser.email)
            deleting_user.delete()
            login(request,teacheruser)
            return redirect('teacherapp:index')
    else:
        form = TeacherSignupForm()

    return render(request,'teacherapp/signup.html',{'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def editinfo(request):
    if request.method == 'POST':
        form = TeacherUpdateForm(request.POST,request.FILES,instance=request.user)
        if form.is_valid():
            teacheruser = form.save()
            teacheruser.save()
            teacheruser.teachable_courses.clear()
            for course in form.cleaned_data['teachable_courses']:   # Looks like manytomany relations can't be saved directly in usercreation forms but in modelforms
                teacheruser.teachable_courses.add(course)
            return redirect('teacherapp:profile')
    else:
        form = TeacherUpdateForm(instance=request.user)

    return render(request,'teacherapp/editinfo.html',{'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def changepassword(request):
    if request.method == 'POST':
        form = TeacherPasswordForm(request.user,request.POST)
        if form.is_valid():
            teacheruser = form.save()
            return redirect('teacherapp:profile')
    else:
        form = TeacherPasswordForm(request.user)

    return render(request,'teacherapp/changepassword.html',{'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def index(request):
    courses = []
    for course in request.user.courses_teaching.all():
        if course.classplans.exists():
            remaining_classdates = [classplan.classdate for classplan in course.classplans.all() if
                                   classplan.classdate >= datetime.date.today()]
        else:
            remaining_classdates = []

        assignments = []
        for assignment in course.get_assignments():
            assignmentdata = {}
            assignmentdata['y'] = str(assignment.classplan.classdate)
            assignmentdata['a'] = assignment.submissions.count()
            assignments.append(assignmentdata)

        completed_tests = [test for test in course.get_tests() if test.results.exists()]
        tests = []
        for test in completed_tests:
            avg_marks = 0  # to account for absentees
            for result in test.results.all():
                avg_marks += result.marks_obtained
            avg_marks = avg_marks/test.results.count()
            testdict = {
                'y': str(test.classplan.classdate),
                'a': avg_marks
            }
            tests.append(testdict)

        coursedata = {
            'data':course,
            'remaining_classdates':remaining_classdates,
            'assignments':assignments,
            'tests':tests,
            'completed_tests': completed_tests
        }
        courses.append(coursedata)

    context = {
        'courses':courses
    }

    return render(request,'teacherapp/index.html',context)


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def profile(request):
    return render(request,'teacherapp/profile.html')


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def courselist(request):
    courses = request.user.courses_teaching.all()
    return render(request,'teacherapp/courselist.html',{'courses':courses})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def studentlist(request):
    courses = request.user.courses_teaching.all()
    if request.method == 'POST':
        formdata = request.POST
        coursename = formdata['course']
        course = education.Course.objects.get(name=coursename)
        selection = {'course':course.name}
    else:
        course = courses[0]
        selection = {'course':course.name}
    return render(request, 'teacherapp/studentlist.html', {'courses': courses, 'course': course, 'selection': selection})

@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def assignmentlist(request):
    courses = request.user.courses_teaching.all()
    assignments = []
    for eachcourse in courses:
        for each in eachcourse.get_assignments():
            assignments.append(each)
    assignment_count = len(assignments)
    deadline_near = [assignment for assignment in assignments if (assignment.submission_deadline-datetime.date.today()).days <= 5 and (assignment.submission_deadline-datetime.date.today()).days >= 0]
    deadline_crossed_count = len([assignment for assignment in assignments if assignment.submission_deadline < datetime.date.today()])
    deadline_upcoming_count = len([assignment for assignment in assignments if assignment.submission_deadline >= datetime.date.today()])
    context = {
        'courses':courses,
        'assignments':assignments,
        'assignment_count':assignment_count,
        'deadline_near':deadline_near,
        'deadline_crossed_count':deadline_crossed_count,
        'deadline_upcoming_count':deadline_upcoming_count,
    }
    return render(request,'teacherapp/assignmentlist.html',context)


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def testlist(request):
    courses = [];
    results_remaining = [];
    for course in request.user.courses_teaching.all():
        completed_tests = [];
        upcoming_tests = [];
        for test in course.get_tests():
            if test.classplan.classdate < datetime.date.today():
                completed_tests.append(test)
                if not test.results.exists():
                    results_remaining.append(test)
            else:
                upcoming_tests.append(test)

        courses.append({
            'data':course,
            'completed_tests':completed_tests,
            'upcoming_tests':upcoming_tests
        })

    return render(request,'teacherapp/testlist.html',{'courses':courses,'results_remaining':results_remaining})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def handoutlist(request):
    courses = request.user.courses_teaching.all()
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
    return render(request, 'teacherapp/handoutlist.html', context)


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def noticelist(request):
    notices = education.Notice.objects.all()
    return render(request,'teacherapp/noticelist.html',{'notices':notices})

@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def profileanalysis(request):
    student = None
    error = {}
    courses = []
    if request.method == 'POST':
        formdata = request.POST
        rollnumber = formdata['rollno']
        try:
            student = accounts.StudentUser.objects.get(rollno=rollnumber)
            for course in student.get_courses():
                assignments = course.get_assignments()
                submitted_assignments = []
                for assignment in assignments:
                    for each in student.submissions.all():
                        if each.assignment.name == assignment.name:
                            submitted_assignments.append(assignment)
                completed_tests = [test for test in course.get_tests() if test.results.exists()]
                passed_tests = []
                tests = []
                for test in completed_tests:
                    marks_obtained = 0      # to account for absentees
                    for result in test.results.all():
                        if (result.student.rollno == student.rollno):
                            marks_obtained = result.marks_obtained
                            if (result.marks_obtained >= test.passmarks):
                                passed_tests.append(test)
                    testdict = {
                        'y': str(test.classplan.classdate),
                        'a': marks_obtained
                    }
                    tests.append(testdict)
                courses.append({
                    'data': course,
                    'submitted_count': len(submitted_assignments),
                    'not_submitted_count': len(assignments) - len(submitted_assignments),
                    'tests':tests,
                    'passed_count':len(passed_tests),
                    'failed_count':len(completed_tests)-len(passed_tests)
                })
        except accounts.StudentUser.DoesNotExist:
            error = {
                'title': 'Invalid Roll Number :',
                'message': 'There is no student with the specified roll number ! Please enter a valid roll number.'
            }

    else:
        error = {
            'title': 'Info :',
            'message': 'Please enter a valid roll number to check the performance analysis of the student.'
        }

    return render(request, 'teacherapp/profileanalysis.html', {'student': student,'courses':courses,'error':error})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def notifications(request):
    notifications = request.user.notifications.all()
    return render(request,'teacherapp/notifications.html',{'notifications':notifications})
