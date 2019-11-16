from django.shortcuts import render,redirect,HttpResponse,Http404
from datarepo.models import *
import datetime
from django.contrib.auth.decorators import login_required
from adminapp import forms as adminforms
from .forms import *
from datarepo.decorators import check_permission


@login_required(login_url='/login/')
def index(request, coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    return render(request, 'courseapp/index.html', {'course': course})

@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def editinfo(request, coursecode):
    try:
        course_instance = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = adminforms.CourseCreationForm(request.POST,request.FILES,instance=course_instance)
        if form.is_valid():
            course_instance = form.save(commit=False)
            course_instance.save()
            # print(form.cleaned_data['name'])
            # print(form.cleaned_data['teacher'])
            # print(form.cleaned_data['profilepic'])
            return redirect('courseapp:index',coursecode=coursecode)
    else:
        form = adminforms.CourseCreationForm(instance=course_instance)
    return render(request,'courseapp/editinfo.html',{'form':form,'course':course_instance})


@login_required(login_url='/login/')
def syllabus(request,coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    form = ChapterCreationForm(initial={'course':course})
    return render(request, 'courseapp/syllabus.html', {'course':course,'form':form})

@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def addchapter(request,coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = ChapterCreationForm(request.POST)
        if form.is_valid():
            chapter = form.save()
            return HttpResponse('Chapter {} was added successfully to {}'.format(chapter.name,course.name))
    else:
        form = ChapterCreationForm()
    return render(request, 'formbase.html', {'form':form})


@login_required(login_url='/login/')
def courseplan(request,coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    if course.chapters.exists():
        error = None
    else:
        error = {
            'code':'No Syllabus',
            'message':'The administrator has not defined a syllabus for this course yet. Please contact the administrator !',
        }
    return render(request,'courseapp/courseplan.html',{'course':course,'error':error})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def addclass(request, coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = ClassCreationForm(course,request.POST)
        if form.is_valid():
            classplan = form.save(commit=False)
            classplan.course = course
            classplan.save()
            print(form.cleaned_data['classdate'])
            return HttpResponse('Class added successfully on {}'.format(classplan.classdate))
    else:
        form = ClassCreationForm(course)
    return render(request, 'courseapp/classplanform.html', {'form': form,'formID':'form-createclassplan','course':course})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def editclass(request, coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    classID = request.META['HTTP_CLASSID']  # All caps on the request header classID because django does so
    classplan = course.classplans.first()
    for each in course.classplans.all():
        if each.get_id() == classID:
            classplan = each
    initial_classdate = classplan.classdate
    if request.method == 'POST':
        form = ClassCreationForm(course,request.POST,instance=classplan)
        if form.is_valid():
            edited_classplan = form.save(commit=False)
            edited_classplan.course = course
            notif = education.Notification(
                message='Class for {} changed from {} to {}'.format(course.name, initial_classdate,
                                                                    edited_classplan.classdate),
                category='classplan')
            notif.save()
            for student in course.get_students():
                notif.target_students.add(student)
            edited_classplan.save()


            return HttpResponse('Class edited successfully')
    else:
        form = ClassCreationForm(course,instance=classplan)
    return render(request, 'courseapp/classplanform.html', {'form': form,'formID':'form-editclassplan','course':course})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def cancelclass(request, coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    classID = request.META['HTTP_CLASSID']  # All caps on the request header classID because django does so
    cancelled_class = course.classplans.last()
    for each in course.classplans.all():
        if each.get_id() == classID:
            cancelled_class = each
    print('Cancelled class: {}'.format(cancelled_class.get_id()))
    lastclass = course.classplans.last()
    listofclasses = course.classplans.all()
    for day in range(len(listofclasses)-1):
        if listofclasses[day].classdate >= cancelled_class.classdate:
            listofclasses[day].classdate = listofclasses[day+1].classdate
            listofclasses[day].save()
    lastclass.classdate = lastclass.classdate + datetime.timedelta(days=7)
    lastclass.save()
    notif = education.Notification(message='Class of {} on {} has been cancelled'.format(course.name, cancelled_class.classdate),
                                   category='classplan')
    notif.save()
    for student in course.get_students():
        notif.target_students.add(student)
    return HttpResponse('The class has been cancelled and new class dates has been assigned successfully')


@login_required(login_url='/login/')
def assignment(request,coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    error = None
    if not course.classplans.exists():
        error = {
            'code': 'No Class Activity Plan',
            'message': 'The class activity plan for this course has not been finalized yet. Hence, course management is inaccessible until then !',
        }
    if not course.chapters.exists():
        error = {
            'code': 'No Syllabus',
            'message': 'The administrator has not defined a syllabus for this course yet. Please contact the administrator !',
        }
    form = AssignmentCreationForm(course)
    if request.user.profiletype == 'StudentUser':
        submitted_assignments = [submission.assignment for submission in request.user.submissions.filter(assignment__classplan__course=course)]
    else:
        submitted_assignments = []
    return render(request, 'courseapp/assignment.html', {'course': course,'error':error,'form':form,'submitted_assignments':submitted_assignments})


@login_required(login_url='/login/')
def submission(request,coursecode,assignmentpk):
    try:
        course = education.Course.objects.get(code=coursecode)
        assignment = education.Assignment.objects.get(pk=assignmentpk)
    except education.Course.DoesNotExist or education.Assignment.DoesNotExist:
        raise Http404
    submissions = []
    for submission in assignment.submissions.all():
        if submission.submission_date.date() > assignment.submission_deadline:
            remarks = 'Late'
        else:
            remarks = ''
        submissions.append({
            'data':submission,
            'remarks':remarks
        })
    remaining_students = []
    for student in course.get_students():
        try:
            submission = student.submissions.get(assignment__pk=assignment.pk)
        except education.Submission.DoesNotExist:
            remaining_students.append(student)

    return render(request, 'courseapp/submission.html', {'course': course,'submissions':submissions,'remaining_students':remaining_students})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def addassignment(request, coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    given_classplan = None
    try:
        classID = request.META['HTTP_CLASSID']  # All caps on the request header classID because django does so
        given_classplan = course.classplans.first()
        for each in course.classplans.all():
            if each.get_id() == classID:
                given_classplan = each
    except:
        pass
    if request.method == 'POST':
        form = AssignmentCreationForm(course, request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save()
            return HttpResponse('Assignment: "{}" added to {}'.format(assignment.name,assignment.classplan))
    else:
        if given_classplan:
            form = AssignmentCreationForm(course,initial={'classplan':given_classplan})
        else:
            form = AssignmentCreationForm(course)

    # A hack to make the cancel button in the common form perform accordingly
    if given_classplan:
        cancelURL = 'courseapp:courseplan'
    else:
        cancelURL = 'courseapp:assignment'

    return render(request, 'courseapp/classplanform.html', {'form': form,'formID':'form-addassignment','course':course,'cancelURL':cancelURL})


@login_required(login_url='/login/')
@check_permission(profiletype='StudentUser')
def addsubmission(request,coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    try:
        assignID = int(request.META['HTTP_ASSIGNID'])  # All caps on the request header classID because django does so
        given_assignment = course.get_assignments()[0]
        for each in course.get_assignments():
            if each.pk == assignID:
                given_assignment = each
    except:
        return HttpResponse('No valid assignment to submit !')
    if request.method == 'POST':
        try:
            initial = given_assignment.submissions.get(student__rollno=request.user.rollno)
            form = SubmissionForm(request.POST, request.FILES,instance=initial)
        except education.Submission.DoesNotExist:
            form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = given_assignment
            submission.student = request.user
            submission.save()
            return HttpResponse('You have submitted the assignment: {}'.format(given_assignment.name))
    else:
        try:
            initial = given_assignment.submissions.get(student__rollno=request.user.rollno)
            form = SubmissionForm(instance=initial)
        except education.Submission.DoesNotExist:
            form = SubmissionForm()

    return render(request, 'courseapp/classplanform.html', {'form': form,'formID':'form-addsubmission','course':course,'cancelURL':'courseapp:assignment'})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def addhandout(request, coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    given_classplan = None
    try:
        classID = request.META['HTTP_CLASSID']  # All caps on the request header classID because django does so
        given_classplan = course.classplans.first()
        for each in course.classplans.all():
            if each.get_id() == classID:
                given_classplan = each
    except:
        pass
    if request.method == 'POST':
        form = HandoutCreationForm(course, request.POST, request.FILES)
        if form.is_valid():
            handout = form.save()
            return HttpResponse('Handout: "{}" added to {}'.format(handout.name,handout.classplan))
    else:
        if given_classplan:
            form = HandoutCreationForm(course,initial={'classplan':given_classplan})
        else:
            form = HandoutCreationForm(course)

    # A hack to make the cancel button in the common form perform accordingly
    if given_classplan:
        cancelURL = 'courseapp:courseplan'
    else:
        cancelURL = 'courseapp:handout'

    return render(request, 'courseapp/classplanform.html', {'form': form,'formID':'form-addhandout','course':course,'cancelURL':cancelURL})


@login_required(login_url='/login/')
def handout(request,coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    error = None
    if not course.classplans.exists():
        error = {
            'code': 'No Class Activity Plan',
            'message': 'The class activity plan for this course has not been finalized yet. Hence, course management is inaccessible until then !',
        }
    if not course.chapters.exists():
        error = {
            'code': 'No Syllabus',
            'message': 'The administrator has not defined a syllabus for this course yet. Please contact the administrator !',
        }
    form = HandoutCreationForm(course)

    return render(request, 'courseapp/handout.html', {'course': course,'error':error,'form':form})


@login_required(login_url='/login/')
def test(request,coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    error = None
    if not course.classplans.exists():
        error = {
            'code': 'No Class Activity Plan',
            'message': 'The class activity plan for this course has not been finalized yet. Hence, course management is inaccessible until then !',
        }
    if not course.chapters.exists():
        error = {
            'code': 'No Syllabus',
            'message': 'The administrator has not defined a syllabus for this course yet. Please contact the administrator !',
        }
    form = TestCreationForm(course)

    return render(request, 'courseapp/test.html', {'course': course,'error':error,'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def addtest(request, coursecode):
    try:
        course = education.Course.objects.get(code=coursecode)
    except education.Course.DoesNotExist:
        raise Http404
    given_classplan = None
    try:
        classID = request.META['HTTP_CLASSID']  # All caps on the request header classID because django does so
        given_classplan = course.classplans.first()
        for each in course.classplans.all():
            if each.get_id() == classID:
                given_classplan = each
    except:
        pass
    if request.method == 'POST':
        form = TestCreationForm(course, request.POST)
        if form.is_valid():
            test = form.save()
            return HttpResponse('Test: "{}" scheduled for {}'.format(test.name,test.classplan))
    else:
        if given_classplan:
            form = TestCreationForm(course,initial={'classplan':given_classplan})
        else:
            form = TestCreationForm(course)

    # A hack to make the cancel button in the common form perform accordingly
    if given_classplan:
        cancelURL = 'courseapp:courseplan'
    else:
        cancelURL = 'courseapp:test'

    return render(request, 'courseapp/classplanform.html', {'form': form,'formID':'form-addtest','course':course,'cancelURL':cancelURL})


@login_required(login_url='/login/')
def result(request,coursecode,testpk):
    try:
        course = education.Course.objects.get(code=coursecode)
        test = education.Test.objects.get(pk=testpk)
    except education.Course.DoesNotExist or education.Test.DoesNotExist:
        raise Http404
    results = test.results.all()
    results_remaining = []
    for student in course.get_students():
        try:
            result = student.results.get(test__pk=test.pk)
        except education.Result.DoesNotExist:
            results_remaining.append(student)

    return render(request, 'courseapp/result.html', {'course': course,'test':test,'results':results,'results_remaining':results_remaining})


@login_required(login_url='/login/')
@check_permission(profiletype='TeacherUser')
def addresult(request,coursecode,testpk):
    try:
        course = education.Course.objects.get(code=coursecode)
        given_test = education.Test.objects.get(pk=testpk)
    except education.Course.DoesNotExist or education.Test.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = ResultCreationForm(given_test,request.POST, request.FILES)
        if form.is_valid():
            result = form.save(commit=False)
            result.test = given_test
            result.save()
            return HttpResponse('Result of {} for {} registered.'.format(result.test.name,result.student.get_full_name()))
    else:
        form = ResultCreationForm(test=given_test)

    return render(request, 'courseapp/classplanform.html', {'form': form,'formID':'form-addresult','course':course,'cancelURL':'courseapp:test'})
