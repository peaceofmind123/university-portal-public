from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # This is the base user inheriting from the AbstractUser of django. It gets all functionality of
    # the default User model. Also remember to check out auth.py where we define a custom authentication
    # backend to comply with our new User models. This model stores data common to all 3 users
    profiletype = models.CharField(max_length=400)

    def __str__(self):
        if self.profiletype == 'AdminUser':
            return self.username
        else:
            return self.get_full_name()


class AdminUser(User):
    # This model stores data relevant to admin only

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def save(self, *args, **kwargs):
        self.profiletype = 'AdminUser'
        super().save(*args, **kwargs)


class TeacherUser(User):
    # This model stores data relevant to teacher only
    #Note: Since the courses the teacher is actually teaching is a one(Teacher) to many(Courses) relation, it is defined on Course model
    teachable_courses = models.ManyToManyField('Course', related_name='possible_teachers',blank=True)
    profilepic = models.ImageField(verbose_name='Profile Picture',upload_to='teachers/')   #Image will be uploaded to MEDIA_ROOT/teachers
    #Note: Since assignments given by teacher is a one(Teacher) to many(Assignments) relation, it is defined on Assignment model
    # Note: Since tests taken by teacher is a one(Teacher) to many(Tests) relation, it is defined on Test model

    def get_notifications(self):
        if self.notifications.exists():
            if self.notifications.count()>5:
                return list(self.notifications.all())[:5]
            else:
                return list(self.notifications.all())
        else:
            return None

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def save(self, *args, **kwargs):
        self.profiletype = 'TeacherUser'
        super().save(*args, **kwargs)


class StudentUser(User):
    # This model stores data relevant to student only

    batch = models.ForeignKey('Batch',on_delete=models.CASCADE,related_name='students',null=True,blank=True)
    stream = models.ForeignKey('Stream',on_delete=models.CASCADE,related_name='students',null=True,blank=True)
    rollno = models.CharField(max_length=200,unique=True)   # <---- check the form for this model to know the auto generation of this field
    profilepic = models.ImageField(upload_to='students/')   #Image will be uploaded to MEDIA_ROOT/students

    # assignments and test don't need direct relations. Find them by querying using other relations
    # Note: submissions are related by Foreignkey with Submission model to store answer file of assignments
    # results is related by ForeignKey in Result model to store mark obtained in specific test

    def get_marks(self):
        marks = {}
        for mark in self.results.all():
            marks[mark.test.test_id] = mark.marks_obtained
        return marks

    def get_courses(self):
        level = self.batch.level
        if level == 1:  #First Year
            return self.stream.level1courses.all()
        elif level == 2:    #Second Year
            return self.stream.level2courses.all()
        elif level == 3:    #Third Year
            return self.stream.level3courses.all()
        elif level == 4:    #Fourth Year
            return self.stream.level4courses.all()

    def get_courses_count(self):
        return len(self.get_courses())

    def get_notifications(self):
        if self.notifications.exists():
            if self.notifications.count()>5:
                return list(self.notifications.all())[:5]
            else:
                return list(self.notifications.all())
        else:
            return None

    #below should be in form as well
    def save(self, *args, **kwargs):    #save() method is overridden so as to auto-generate the roll number
        try:
            if (not self.rollno) and (self.batch and self.stream):      #This is done so that we do not find roll twice in form submission but it is used in command line data submission
                batch_id = self.batch.batch_id  # like 072,073,074
                stream_id = self.stream.stream_id  # like BCT,BEX,BEL
                starting_rollno = self.stream.startingrollno  # like 400 for BEX, 500 for BCT
                unsigned_std_count = self.batch.unsigned_students.filter(stream__name=self.stream.name).count()  # This finds the number of non signed up students of the stream of the particular batch
                signed_std_count = self.batch.students.filter(stream__name=self.stream.name).count()  # This finds the number of signed up students of the stream of the particular batch
                std_count = unsigned_std_count + signed_std_count
                self.rollno = str(batch_id) + stream_id + str(starting_rollno + std_count + 1)  # note that 1 is added to existing count
        except:
            pass

        self.profiletype = 'StudentUser'
        super().save(*args,**kwargs)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


class TempTeacherUser(models.Model):    # to store the teacher data entered by admin but yet to be signed up
    first_name = models.CharField(max_length=400, verbose_name='First Name', null=False)
    last_name = models.CharField(max_length=400, verbose_name='Surname', null=False)
    email = models.EmailField(max_length=500, null=False, unique=True)
    # Note: I think it's best if admin doesn't chooses what courses the teacher can teach. That
    # is better chosen by teacher when he signs up and admin chooses a teacher for a course later on
    def __str__(self):
        return 'TempTeacher:'+self.first_name

    class Meta:
        verbose_name = 'Unsigned Teacher'
        verbose_name_plural = 'Unsigned Teachers'


class TempStudentUser(models.Model):    # to store the student data entered by admin but yet to be signed up
    first_name = models.CharField(max_length=400,verbose_name='First Name',null=False)
    last_name = models.CharField(max_length=400,verbose_name='Surname',null=False)
    email = models.EmailField(max_length=500,null=False,unique=True)
    rollno = models.CharField(max_length=200,blank=True)
    batch = models.ForeignKey('Batch',on_delete=models.CASCADE,related_name='unsigned_students')
    stream = models.ForeignKey('Stream',on_delete=models.CASCADE,related_name='unsigned_students')

    def setrollno(self):
        try:
            if (not self.rollno) and (self.batch and self.stream):      #This is done so that we do not find roll twice in form submission but it is used in command line data submission
                batch_id = self.batch.batch_id  # like 072,073,074
                stream_id = self.stream.stream_id  # like BCT,BEX,BEL
                starting_rollno = self.stream.startingrollno  # like 400 for BEX, 500 for BCT
                unsigned_std_count = self.batch.unsigned_students.filter(stream__name=self.stream.name).count()  # This finds the number of non signed up students of the stream of the particular batch
                signed_std_count = self.batch.students.filter(stream__name=self.stream.name).count()    # This finds the number of signed up students of the stream of the particular batch
                std_count = unsigned_std_count + signed_std_count
                self.rollno = str(batch_id) + stream_id + str(starting_rollno + std_count + 1)  # note that 1 is added to existing count
        except:
            pass

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.setrollno()
        super().save()

    def __str__(self):
        return 'TempStudent:'+self.rollno

    class Meta:
        verbose_name = 'Unsigned Student'
        verbose_name_plural = 'Unsigned Students'
