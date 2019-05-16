from django.contrib.auth.forms import UserCreationForm
from django import forms
from datarepo.models import *

class AdminSignupForm(UserCreationForm):
    #Signup Form for admin
    class Meta:
        model = accounts.AdminUser
        fields = ['username','email','password1','password2']



class TeacherCreationForm(forms.ModelForm):
    # Here, we need to make custom validation for email field because entered email should not match with any of TeacherUser of TempTeacherUser
    def clean_email(self):
        entered_email = self.cleaned_data['email']
        try:
            duplicate_teacher = accounts.TempTeacherUser.objects.get(email=entered_email)
            raise forms.ValidationError('A teacher with the entered email is already registered !')
        except accounts.TempTeacherUser.DoesNotExist:
            try:
                duplicate_user = accounts.User.objects.get(email=entered_email)
                raise forms.ValidationError('The entered email already belongs to a user signed up to the portal !')
            except accounts.User.DoesNotExist:
                return entered_email        # Important --- value must be returned. If pass is used, null will be used in the field after one error.

    class Meta:
        model = accounts.TempTeacherUser
        fields = ['first_name','last_name','email']


class StudentCreationForm(forms.ModelForm):
    # Here, we need to make custom validation for email field because entered email should not match with any of TeacherUser of TempTeacherUser
    def clean_email(self):
        entered_email = self.cleaned_data['email']
        try:
            duplicate_student = accounts.TempStudentUser.objects.get(email=entered_email)
            raise forms.ValidationError('A student with the entered email is already registered !')
        except accounts.TempStudentUser.DoesNotExist:
            try:
                duplicate_user = accounts.User.objects.get(email=entered_email)
                raise forms.ValidationError('The entered email already belongs to a user signed up to the portal !')
            except accounts.User.DoesNotExist:
                return entered_email        # Important --- value must be returned. If pass is used, null will be used in the field after one error.

    class Meta:
        model = accounts.TempStudentUser
        fields = ['batch','stream','first_name','last_name','email']


class BatchCreationForm(forms.ModelForm):
    class Meta:
        model = education.Batch
        fields = ['batch_id','streams',]
        widgets = {
            'streams': forms.CheckboxSelectMultiple,
        }
        help_texts = {
            'batch_id': 'Enter the year of enrollment in B.S. for the new batch of students. This will be used as the unique Batch ID',
            'streams': 'Choose the different streams in which the students of this batch can enroll.'
        }


class StreamCreationForm(forms.ModelForm):
    class Meta:
        model = education.Stream
        fields = ['stream_id','name','duration_years','startingrollno','level1courses',
                  'level2courses','level3courses','level4courses',]
        widgets = {
            'level1courses': forms.CheckboxSelectMultiple,
            'level2courses': forms.CheckboxSelectMultiple,
            'level3courses': forms.CheckboxSelectMultiple,
            'level4courses': forms.CheckboxSelectMultiple,
        }


class CourseCreationForm(forms.ModelForm):
    class Meta:
        model = education.Course
        fields = ['code','name','totalmarks','teacher','profilepic']
        help_texts = {
            'teacher':'Assign a teacher to teach the course from the list of teachers.',
            'profilepic':'Upload a picture that best represents the notion of the course.',
        }


class NoticeCreationForm(forms.ModelForm):
    class Meta:
        model = education.Notice
        fields = ['category','title','description']
        help_texts = {
            'category':'Choose which category of information the notice is trying to convey',
        }
        widgets = {
            'description':forms.Textarea,
        }
