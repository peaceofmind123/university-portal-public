from django.db import models
from .accounts import *
import datetime

class Stream(models.Model):
    stream_id = models.CharField(max_length=200,primary_key=True,verbose_name='Stream ID')
    name = models.CharField(max_length=500)
    duration_years = models.PositiveIntegerField(default=4, verbose_name='Duration in years')
    startingrollno = models.PositiveIntegerField(verbose_name='Starting Roll Number', unique=True)
    level1courses = models.ManyToManyField('Course', related_name='level1streams',verbose_name='Courses taught in 1st year',blank=True)
    level2courses = models.ManyToManyField('Course', related_name='level2streams',verbose_name='Courses taught in 2nd year',blank=True)
    level3courses = models.ManyToManyField('Course', related_name='level3streams',verbose_name='Courses taught in 3rd year',blank=True)
    level4courses = models.ManyToManyField('Course', related_name='level4streams',verbose_name='Courses taught in 4th year',blank=True)

    def get_level1students(self):
        return self.students.filter(batch__level=1)

    def get_level2students(self):
        return self.students.filter(batch__level=2)

    def get_level3students(self):
        return self.students.filter(batch__level=3)

    def get_level4students(self):
        return self.students.filter(batch__level=4)

    def __str__(self):
        return self.name
    # Note: students is also related by ForeignKey in StudentUser model
    # Note: unsigned_students is also related by ForeignKey in TempStudentUser model
    # Note: courses is related by ManytoManyField in Course
    # ------- Reminder for form implementation ----> Make a field for selecting courses and building relation
    # between streams and courses explicitly


class Batch(models.Model):
    LEVEL_CHOICES = (
        (1, "First Year"),
        (2, "Second Year"),
        (3, "Third Year"),
        (4, "Fourth Year"),
    )
    batch_id = models.IntegerField(verbose_name='Batch ID', primary_key=True)
    level = models.IntegerField(choices=LEVEL_CHOICES,default=1,blank=True)
    streams = models.ManyToManyField('Stream',verbose_name='Streams associated with the batch', related_name='batches')
    #Note:  students are related by Foreignkey in respective models

    class Meta:
        ordering = ('-level',)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # if Batch.objects.count() == 4:      #Comment these lines for changing data through djadmin
        #     outgoing_batch = Batch.objects.first()
        #     outgoing_batch.delete()
        # old_batches = Batch.objects.all()
        # for each in old_batches:
        #     each.level = each.level+1
        super().save()

    def __str__(self):
        return str(self.batch_id)


class Course(models.Model):
    code = models.CharField(max_length=300,primary_key=True)
    name = models.CharField(max_length=400,null=False)
    totalmarks = models.PositiveIntegerField(verbose_name='Total marks',default=100)
    teacher = models.ForeignKey('TeacherUser', on_delete=models.SET_NULL,
                                verbose_name='Teacher assigned',null=True, blank=True,
                                related_name='courses_teaching')  # SET_NULL used in place of CASCADE so that if the teacher is deleted, the course won't get deleted
    profilepic = models.ImageField(upload_to='courses/',verbose_name='Course Picture')

    def get_assignments(self):
        assignments = []
        if self.classplans.exists():
            for classplan in self.classplans.all():
                try:
                    if classplan.assignment is not None:
                        assignments.append(classplan.assignment)
                except:
                    pass
        return assignments

    def get_handouts(self):
        handouts = []
        if self.classplans.exists():
            for classplan in self.classplans.all():
                try:
                    if classplan.handout is not None:
                        handouts.append(classplan.handout)
                except:
                    pass
        return handouts

    def get_tests(self):
        tests = []
        if self.classplans.exists():
            for classplan in self.classplans.all():
                try:
                    if classplan.test is not None:
                        tests.append(classplan.test)
                except:
                    pass
        return tests

    def get_courseplan(self):   # to return the dict of classplan, note that this might be required in course pages or student pages
        return self.classplans.all()

    def get_streams(self):
        streams = []
        if(self.level1streams.exists()):
            for stream in self.level1streams.all():
                streams.append(stream)
        if (self.level2streams.exists()):
            for stream in self.level2streams.all():
                streams.append(stream)
        if (self.level3streams.exists()):
            for stream in self.level3streams.all():
                streams.append(stream)
        if (self.level4streams.exists()):
            for stream in self.level4streams.all():
                streams.append(stream)
        return streams

    def get_students(self):
        students = []
        for stream in self.level1streams.all():
            for student in stream.get_level1students():
                students.append(student)
        for stream in self.level2streams.all():
            for student in stream.get_level2students():
                students.append(student)
        for stream in self.level3streams.all():
            for student in stream.get_level3students():
                students.append(student)
        for stream in self.level4streams.all():
            for student in stream.get_level4students():
                students.append(student)
        return students

    def get_students_count(self):
        students = self.get_students()
        return len(students)

    def get_next_classdate(self):
        if self.classplans.exists():
            for classplan in self.classplans.all():
                if classplan.classdate >= datetime.date.today():
                    return classplan.classdate

    def get_completed_chapters(self):
        return [chapter for chapter in self.chapters.all() if chapter.is_completed()]

    def get_completed_chapters_count(self):
        return len(self.get_completed_chapters())

    def get_completion_percent(self):
        total = self.chapters.all()
        completed = self.get_completed_chapters()
        if total:   # To account for zero division errors when no syllabus has been set.
            percent = int(len(completed)/len(total)*100)
        else:
            percent = 0
        return percent


    def __str__(self):
        return self.name

    # Note: possible_teachers is linked as ManytoManyField in TeacherUser model
    # Note: chapters are linked as Foreignkey on Chapter model
    #----> Reminder for form implementation: make a custom field to take input for chapter name and description
    # Then, the chapter is to be created with that info and related with this course by its foreignkey
    # Note: classplans are linked as Foreignkey on ClassPlan model
    # ----> Reminder for form implementation: make a custom field to take input for many classplans with necessary fields
    # Then, each classplan is to be created with that info and related with this course by its foreignkey


class Chapter(models.Model):
    name = models.CharField(max_length=300,null=False)
    description = models.CharField(max_length=2000,null=True)
    course = models.ForeignKey('Course',on_delete=models.CASCADE,related_name='chapters')
    #classplans is linked as Foreignkey in ClassPlan model i.e the classplans where this chapter will be taught
    #featuring_tests is related by ManytoManyField in Test model

    def get_assignments(self):
        assignments = []
        if self.classplans.exists():
            for classplan in self.classplans.all():
                try:
                    if classplan.assignment is not None:
                        assignments.append(classplan.assignment)
                except:
                    pass
        return assignments

    def get_handouts(self):
        handouts = []
        if self.classplans.exists():
            for classplan in self.classplans.all():
                try:
                    if classplan.handout is not None:
                        handouts.append(classplan.handout)
                except:
                    pass
        return handouts

    def is_completed(self):
        if self.classplans.exists():
            if self.classplans.last().classdate < datetime.date.today():
                return True
        else:
            return False

    def __str__(self):
        return self.name


class ClassPlan(models.Model):
    classdate = models.DateField(verbose_name='Class Date')
    course = models.ForeignKey('Course',on_delete=models.CASCADE,related_name='classplans',blank=True)
    chapter = models.ForeignKey('Chapter',on_delete=models.CASCADE,related_name='classplans')

    class Meta:
        ordering = ('classdate',)

    def __str__(self):
        return 'Class for {} on {}'.format(self.course.name,str(self.classdate))

    def get_id(self):
        try:
            classID = self.course.code +'DATE'+str(self.classdate).replace('-','')
            return classID
        except:
            return 'classID'

    def is_completed(self):
        if self.classdate < datetime.date.today():
            return True
        else:
            return False

    # assignment is related by OnetoOneField in Assignment model
    # test is related by OnetoOneField in Test model
    # handouts is related by OnetoOne in Handout model
    # Note: ClassPlan obj exists by residing inside course obj only. In other words, in client-side
    # classplans are to be created/edited only through courses
    # ----?? Important ??---- must find a way to prevent many classplans having the same classdate because a day can only have certain classes


class Assignment(models.Model):
    name = models.CharField(max_length=500,null=False)
    description = models.CharField(max_length=2000,null=True,blank=True)
    published_date = models.DateField(auto_now_add=True,verbose_name='Published Date')
    submission_deadline = models.DateField(verbose_name='Submission Deadline',null=False)
    classplan = models.OneToOneField('ClassPlan',on_delete=models.CASCADE,related_name='assignment')
    question_file = models.FileField(upload_to='assignments/questions',verbose_name='Attached File',blank=True,null=True)

    # Note: submissions is related by Foreignkey in Submission model
    def get_course(self):
        if self.classplan:
            return self.classplan.course
        else:
            return None

    def get_chapter(self):
        if self.classplan:
            return self.classplan.chapter
        else:
            return None

    def get_studentlist(self):
        return self.classplan.course.get_students()

    def __str__(self):
        return self.name


    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        notif = Notification(message='New Assignment:'+self.name,category='assignment')
        notif.save()
        for student in self.get_studentlist():
            notif.target_students.add(student)



class Submission(models.Model):     # This model is made so that we can relate submission files of assignment to students and assignments
    answer_file = models.FileField(upload_to='assignments/answers',verbose_name='Answer File')
    assignment = models.ForeignKey('Assignment',on_delete=models.CASCADE,related_name='submissions',blank=True)
    student = models.ForeignKey('StudentUser',on_delete=models.CASCADE,related_name='submissions',blank=True)
    submission_date = models.DateTimeField(verbose_name='Date of Submission',auto_now_add=True,null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        try:
            notif = Notification(message='New Submission from:'+self.student.rollno,category='submission')
            notif.save()
            notif.target_teachers.add(self.assignment.classplan.course.teacher)
        except:
            pass

    def __str__(self):
        return '{} submitted {}'.format(self.student.username,self.assignment.name)


class Handout(models.Model):
    name = models.CharField(max_length=500, null=False)
    description = models.CharField(max_length=2000, null=True, blank=True)
    published_date = models.DateField(auto_now_add=True, verbose_name='Published Date')
    classplan = models.OneToOneField('ClassPlan', on_delete=models.CASCADE,related_name='handout')
    attached_file = models.FileField(verbose_name='Handout Document',upload_to='handouts/',null=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        notif = Notification(message='New Handout:'+self.name,category='handout')
        notif.save()
        for student in self.classplan.course.get_students():
            notif.target_students.add(student)


class Test(models.Model):
    name = models.CharField(max_length=500, null=False)
    fullmarks = models.PositiveIntegerField(verbose_name='Full marks',default=20)
    passmarks = models.PositiveIntegerField(verbose_name='Pass marks',default=8)
    classplan = models.OneToOneField('ClassPlan',on_delete=models.CASCADE)
    test_id = models.CharField(max_length=300,blank=True,primary_key=True)     #should be auto-generated before save
    chapters_to_study = models.ManyToManyField('Chapter',related_name='featuring_tests',verbose_name='Chapters in Syllabus')
    # results is related by ForeignKey in Result model

    def get_studentlist(self):
        return self.classplan.course.get_students()

    def get_studentwithmarks(self):
        marks = {}
        for result in self.results.all():
            marks[result.student.rollno] = result.marks_obtained
        return marks

    def set_test_id(self):
        try:
            if (not self.test_id) and self.classplan:
                course = self.classplan.course
                test_count = len(course.get_tests())  # too much querying, find a better way
                self.test_id = '{}-Test{}'.format(course.code, str(test_count + 1))
        except:
            pass

    def get_id(self):
        new_id = self.test_id.replace('-','')
        return new_id

    def get_passed_count(self):
        passed_count = 0
        for result in self.results.all():
            if result.marks_obtained >= self.passmarks:
                passed_count += 1
        return passed_count

    def get_failed_count(self):
        return self.results.count()-self.get_passed_count()



    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.set_test_id()
        super().save()

    def __str__(self):
        return self.name


class Result(models.Model):       #This model is to relate test,the student who gave it and marks obtained
    test = models.ForeignKey(Test,on_delete=models.CASCADE,related_name='results')
    student = models.ForeignKey('StudentUser',on_delete=models.CASCADE,related_name='results')
    marks_obtained = models.PositiveIntegerField(verbose_name='Obtained Marks',default=8,null=True)    #null for absentees

    def passorfail(self):
        if self.marks_obtained:
            if self.marks_obtained >= self.test.passmarks:
                return 'Passed'
            else:
                return 'Failed'
        else:
            return 'Failed'

    def __str__(self):
        return "{}'s result of {}".format(self.student.username,self.test.name)


class Notice(models.Model):
    CATEGORY_CHOICES = (
        ("Co-curricular", "Co-curricular"),
        ("Admission", "Admission"),
        ("Exam", "Exam"),
        ("Holiday", "Holiday"),
        ("General", "General"),
    )
    title = models.CharField(max_length=500)
    category = models.CharField(choices=CATEGORY_CHOICES,max_length=100)
    description = models.CharField(max_length=2000)
    published_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-published_date',)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        notif = Notification(message=self.title,category='notice')
        notif.save()
        for student in StudentUser.objects.all():
            notif.target_students.add(student)
        for teacher in TeacherUser.objects.all():
            notif.target_teachers.add(teacher)

        print(notif.target_students.all())
        print(notif.target_teachers.all())

    def __str__(self):
        return self.title


class Notification(models.Model):
    message = models.CharField(max_length=500)
    category = models.CharField(max_length=500)
    target_students = models.ManyToManyField('StudentUser',related_name='notifications')
    target_teachers = models.ManyToManyField('TeacherUser',related_name='notifications')
    created_date = models.DateTimeField(auto_now_add=True)
    redirect_url = models.CharField(max_length=500)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return self.message