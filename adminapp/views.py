from django.shortcuts import render,redirect,Http404,HttpResponse
from .forms import *
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from datarepo.models import *
from datarepo.decorators import check_permission
from django.db.models import Q


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def index(request):
    streams = list(education.Stream.objects.all())
    batches = list(education.Batch.objects.all())
    courses = list(education.Course.objects.all())
    students = list(accounts.StudentUser.objects.all())
    teachers = list(accounts.TeacherUser.objects.all())
    barchartdata = []
    for batch in batches:
        batchdata = {}
        batchdata['y'] = str(batch.batch_id)
        for stream in streams:
            batchdata[stream.stream_id] = stream.students.filter(batch__batch_id=batch.batch_id).count()
        barchartdata.append(batchdata)
    barchartlabel = {
        'xkey': 'y',
        'ykeys': [stream.stream_id for stream in streams],
        'labels': [stream.stream_id for stream in streams],
    }
    context = {
        'streams': streams,
        'batches': batches,
        'courses': courses,
        'students': students,
        'teachers': teachers,
        'barchart': {
            'data': barchartdata,
            'label': barchartlabel
        }
    }
    return render(request,'adminapp/index.html',context)


def signup(request):
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            adminuser = form.save()
            adminuser.profiletype = 'AdminUser'
            adminuser.save()
            login(request,adminuser)
            return redirect('adminapp:index')
    else:
        form = AdminSignupForm()

    return render(request,'adminapp/signup.html',{'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def studentlist(request):
    batches = education.Batch.objects.all()
    streams = education.Stream.objects.all()
    if request.method == 'POST':
        formdata = request.POST
        batch_id = int(formdata['batch'])
        stream_id = formdata['stream']
        studentlist = accounts.StudentUser.objects.filter(batch__batch_id=batch_id,stream__stream_id=stream_id)
        unsignedlist = accounts.TempStudentUser.objects.filter(batch__batch_id=batch_id, stream__stream_id=stream_id)
        selection = {
            'batch':batch_id,
            'stream':stream_id
        }
    else:
        selection = {
            'batch':batches[0].batch_id,
            'stream':streams[0].stream_id
        }
        studentlist = accounts.StudentUser.objects.filter(batch__batch_id=batches[0].batch_id, stream__stream_id=streams[0].stream_id)
        unsignedlist = accounts.TempStudentUser.objects.filter(batch__batch_id=batches[0].batch_id, stream__stream_id=streams[0].stream_id)

    selected_batch = education.Batch.objects.get(batch_id=selection['batch'])
    selected_stream = education.Stream.objects.get(stream_id=selection['stream'])

    if selected_batch.streams.filter(stream_id=selected_stream.stream_id).count():
        error = None
    else:
        error = {
            'code': 'Invalid Combination',
            'message': 'The entered stream: {} is not taught to the students of the batch: {}'.format(selected_stream.stream_id,selected_batch.batch_id)
        }

    form = StudentCreationForm(initial={'batch':selected_batch,'stream':selected_stream})

    return render(request,'adminapp/studentlist.html',{'batches':batches,
                                                       'streams':streams,
                                                       'studentlist':studentlist,
                                                       'unsignedlist':unsignedlist,
                                                       'selection':selection,
                                                       'form':form,
                                                       'error':error})

@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def addstudent(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            student = form.save()
            print(form.cleaned_data['first_name'])
            print(form.cleaned_data['email'])
            print(form.cleaned_data['batch'])
            return HttpResponse('New student, {} {} has been successfully registered with roll number: {}. However, the student needs to sign up and provide login credentials to begin using the portal.'.format(form.cleaned_data['first_name'],form.cleaned_data['last_name'],student.rollno))
    else:
        form = StudentCreationForm()
    return render(request, 'formbase.html', {'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def addbatch(request):
    # Please note that while adding a new batch, we need to destroy the oldest batch and also reset all the courses and submissions
    if request.method == 'POST':
        form = BatchCreationForm(request.POST)
        if form.is_valid():
            batch = form.save()
            batch.save()
            return redirect('adminapp:studentlist')
    else:
        form = BatchCreationForm()
    return render(request, 'adminapp/addbatch.html', {'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def streamlist(request):
    streams = education.Stream.objects.all()
    return render(request,'adminapp/streamlist.html',{'streams':streams})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def addstream(request):
    if request.method == 'POST':
        form = StreamCreationForm(request.POST)
        if form.is_valid():
            stream = form.save()
            return redirect('adminapp:streaminfo',stream_id=stream.stream_id)
    else:
        form = StreamCreationForm()
    return render(request,'adminapp/addstream.html',{'form':form})

@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def streaminfo(request,stream_id):
    try:
        stream = education.Stream.objects.get(stream_id=stream_id)
    except education.Stream.DoesNotExist:
        raise Http404
    return render(request,'adminapp/streaminfo.html',{'stream':stream})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def editstream(request,stream_id):
    try:
        stream_instance = education.Stream.objects.get(stream_id=stream_id)
    except education.Stream.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = StreamCreationForm(request.POST,instance=stream_instance)
        if form.is_valid():
            stream_instance.name = form.cleaned_data['name']
            stream_instance.startingrollno = form.cleaned_data['startingrollno']
            stream_instance.save()
            stream_instance.level1courses.clear()
            for course in form.cleaned_data['level1courses']:
                stream_instance.level1courses.add(course)
            stream_instance.level2courses.clear()
            for course in form.cleaned_data['level2courses']:
                stream_instance.level2courses.add(course)
            stream_instance.level3courses.clear()
            for course in form.cleaned_data['level3courses']:
                stream_instance.level3courses.add(course)
            stream_instance.level4courses.clear()
            for course in form.cleaned_data['level4courses']:
                stream_instance.level4courses.add(course)

            return redirect('adminapp:streaminfo',stream_id=stream_instance.stream_id)
    else:
        form = StreamCreationForm(instance=stream_instance)
    return render(request,'adminapp/editstream.html',{'stream':stream_instance,'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def courselist(request):
    courses = education.Course.objects.all()
    return render(request, 'adminapp/courselist.html', {'courses': courses})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def addcourse(request):
    if request.method == 'POST':
        print(request.POST)
        form = CourseCreationForm(request.POST,request.FILES)
        if form.is_valid():
            course = form.save()
            return redirect('courseapp:index',coursecode=course.code)
    else:
        form = CourseCreationForm()
    return render(request,'adminapp/addcourse.html',{'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def teacherlist(request):
    teachers = accounts.TeacherUser.objects.all()
    unsigned_teachers = accounts.TempTeacherUser.objects.all()
    form = TeacherCreationForm()
    return render(request,'adminapp/teacherlist.html',
                  {'teachers':teachers,'unsigned_teachers':unsigned_teachers,'form':form})


@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def addteacher(request):
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            return HttpResponse('New teacher, {} {} has been successfully registered. However, the teacher needs to sign up and provide login credentials to begin using the portal.'.format(form.cleaned_data['first_name'],form.cleaned_data['last_name']))
    else:
        form = TeacherCreationForm()
    return render(request, 'formbase.html', {'form':form})



@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def noticelist(request):
    notices = education.Notice.objects.all()
    return render(request,'adminapp/noticelist.html',{'notices':notices})

@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
def addnotice(request):
    if request.method == 'POST':
        form = NoticeCreationForm(request.POST)
        if form.is_valid():
            notice = form.save()
            return HttpResponse('New notice: "{}" added. All the teachers and students have been notified'.format(notice.title))
    else:
        form = NoticeCreationForm()
    return render(request,'formbase.html',{'form':form,'formID':'form-addnotice','returnURL':'adminapp:noticelist'})

@login_required(login_url='/login/')
@check_permission(profiletype='AdminUser')
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
                    'failed_count':len(tests)-len(passed_tests)
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

    return render(request, 'adminapp/profileanalysis.html', {'student': student,'courses':courses,'error':error})
