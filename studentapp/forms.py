from django.contrib.auth.forms import UserCreationForm,UserChangeForm,PasswordChangeForm
from django import forms
from datarepo.models import *


class StudentSignupForm(UserCreationForm):

    def clean(self):
        formdata = self.cleaned_data
        entered_rollno = formdata.get('rollno')
        try:
            registered_student = accounts.TempStudentUser.objects.get(rollno=entered_rollno)
            registered_name = registered_student.first_name+' '+registered_student.last_name
            registered_email = registered_student.email
            entered_name = formdata.get('first_name')+' '+formdata.get('last_name')
            entered_email = formdata.get('email')
            if (registered_name != entered_name) or (registered_email != entered_email):
                raise forms.ValidationError("The roll number and other credentials don't match in the records")
            return formdata
        except accounts.TempStudentUser.DoesNotExist:
            try:
                signedup_student = accounts.StudentUser.objects.get(rollno=entered_rollno)
                raise forms.ValidationError('Student with the entered roll number has already signed up !')
            except accounts.StudentUser.DoesNotExist:
                raise forms.ValidationError('No student with such roll number has been admitted yet')

    class Meta:
        model = accounts.StudentUser
        fields = ['first_name','last_name','rollno','email','username','password1','password2','profilepic']
        help_texts = {
            'profilepic':'Upload a picture to use as your account profile picture',
        }
        

class StudentUpdateForm(UserChangeForm):

    def clean_email(self):
        entered_email = self.cleaned_data.get('email')
        if(not entered_email):
            raise forms.ValidationError('This field is required !')
        duplicate_users = accounts.User.objects.filter(email=entered_email).exclude(username=self.cleaned_data['username']).count()
        if duplicate_users:
            raise forms.ValidationError('This email address already belongs to another user !')
        return entered_email

    class Meta:
        model = accounts.StudentUser
        fields = ['username','rollno','first_name','last_name','email','profilepic','password']
        help_texts = {
            'profilepic': 'Upload a picture to use as your account profile picture',
        }


class StudentPasswordForm(PasswordChangeForm):
    class Meta:
        model = accounts.StudentUser
