from django import forms
from datarepo.models import *


class ChapterCreationForm(forms.ModelForm):
    class Meta:
        model = education.Chapter
        fields = ['name','description','course']


class ClassCreationForm(forms.ModelForm):

    def __init__(self,course,*args,**kwargs):
        self.relatedCourse = course
        super().__init__(*args,**kwargs)
        self.fields['chapter'].queryset = education.Chapter.objects.filter(course__code=course.code)
        # The above line of code will limit the options in chapter select field to that of the specific course

    def clean_classdate(self):  # Validation to ensure no two classes of same course fall on the same day
        entered_date = self.cleaned_data['classdate']
        try:    # for the editing case
            duplicate_class = self.relatedCourse.classplans.filter(classdate=entered_date).exclude(
                pk=self.instance.pk).count()
            if duplicate_class:
                raise forms.ValidationError('There is already a class for {} on this date'.format(self.relatedCourse.name))
            return entered_date
        except: # for the creation case as exception will be raised for self.instance
            duplicate_class = self.relatedCourse.classplans.filter(classdate=entered_date).count()
            if duplicate_class:
                raise forms.ValidationError(
                    'There is already a class for {} on this date'.format(self.relatedCourse.name))
            return entered_date

    class Meta:
        model = education.ClassPlan
        fields = ['classdate','chapter']
        widgets = {
            'classdate':forms.SelectDateWidget,
        }
        help_texts={
            'chapter':'Choose which chapter will be covered on this class day',
        }


class AssignmentCreationForm(forms.ModelForm):
    def __init__(self,course,*args,**kwargs):
        self.relatedCourse = course
        super().__init__(*args,**kwargs)
        self.fields['classplan'].queryset = education.ClassPlan.objects.filter(course__code=course.code)
        # The above line limits the classplan options

    class Meta:
        model = education.Assignment
        fields = ['classplan','name','description','submission_deadline','question_file']
        widgets = {
            'submission_deadline':forms.SelectDateWidget,
        }


class HandoutCreationForm(forms.ModelForm):
    def __init__(self,course,*args,**kwargs):
        self.relatedCourse = course
        super().__init__(*args,**kwargs)
        self.fields['classplan'].queryset = education.ClassPlan.objects.filter(course__code=course.code)
        # The above line limits the classplan options

    class Meta:
        model = education.Handout
        fields = ['classplan','name','description','attached_file']


class TestCreationForm(forms.ModelForm):
    def __init__(self,course,*args,**kwargs):
        self.relatedCourse = course
        super().__init__(*args,**kwargs)
        self.fields['classplan'].queryset = education.ClassPlan.objects.filter(course__code=course.code)
        # The above line limits the classplan options
        self.fields['chapters_to_study'].queryset = education.Chapter.objects.filter(course__code=course.code)
        # The above line limits the chapters' options

    class Meta:
        model = education.Test
        fields = ['classplan','name','fullmarks','passmarks','chapters_to_study']


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = education.Submission
        fields = ['answer_file',]
        help_texts = {
            'answer_file': 'Upload the file containing the solution of the assignment.'
        }


class ResultCreationForm(forms.ModelForm):
    def __init__(self,test,*args,**kwargs):
        self.relatedTest = test
        super().__init__(*args,**kwargs)
        self.fields['student'].queryset = accounts.StudentUser.objects.filter(rollno__in=[each.rollno for each in test.classplan.course.get_students()])

    def clean_student(self):
        entered_student = self.cleaned_data['student']
        try:
            initial_result = entered_student.results.get(test__pk=self.relatedTest.pk)
            self.instance = initial_result
        except education.Result.DoesNotExist:
            pass
        return entered_student

    class Meta:
        model = education.Result
        fields = ['student','marks_obtained',]
        help_texts = {
            'student':'Choose the student whose result is to be added or changed.'
        }