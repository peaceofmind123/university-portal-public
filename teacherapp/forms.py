from django.contrib.auth.forms import UserCreationForm,UserChangeForm,PasswordChangeForm
from django import forms
from datarepo.models import *


class TeacherSignupForm(UserCreationForm):

    def clean(self):
        formdata = self.cleaned_data
        try:
            entered_email = self.cleaned_data.get('email')
            registered_teacher = accounts.TempTeacherUser.objects.get(email=entered_email)
            registered_name = registered_teacher.first_name+' '+registered_teacher.last_name
            entered_name = formdata.get('first_name')+' '+formdata.get('last_name')
            if registered_name != entered_name:
                raise forms.ValidationError("The email address and the name doesn't match in the records")
            return formdata
        except accounts.TempTeacherUser.DoesNotExist:
            raise forms.ValidationError('No Teacher with such email address has been recruited yet')

    class Meta:
        model = accounts.TeacherUser
        fields = ['first_name','last_name','email','username','password1','password2','teachable_courses','profilepic']
        help_texts = {
            'teachable_courses':'Select the list of courses you are capable of teaching',
            'profilepic':'Upload a picture to use as your account profile picture',
        }
        widgets = {
            'teachable_courses':forms.CheckboxSelectMultiple,
        }


class TeacherUpdateForm(UserChangeForm):

    def clean_email(self):
        entered_email = self.cleaned_data.get('email')
        if (not entered_email):
            raise forms.ValidationError('This field is required !')
        duplicate_users = accounts.User.objects.filter(email=entered_email).exclude(username=self.cleaned_data['username']).count()
        if duplicate_users:
            raise forms.ValidationError('This email address already belongs to another user !')
        return entered_email

    class Meta:
        model = accounts.TeacherUser
        fields = ['username','first_name','last_name','email','teachable_courses','profilepic','password']
        help_texts = {
            'teachable_courses': 'Select the list of courses you are capable of teaching',
            'profilepic': 'Upload a picture to use as your account profile picture',
        }
        widgets = {
            'teachable_courses': forms.CheckboxSelectMultiple,
            'password': forms.PasswordInput,
        }


class TeacherPasswordForm(PasswordChangeForm):
    class Meta:
        model = accounts.TeacherUser
