from django.contrib import admin
from django.contrib.auth.admin import UserAdmin,UserChangeForm,UserCreationForm
from .models import *
# Register your models here.


class AdminUserAdmin(UserAdmin):
    model = accounts.AdminUser


class StudentUserAdmin(UserAdmin):
    model = accounts.StudentUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('rollno','batch','stream','profilepic',)}),
    )


class TeacherUserAdmin(UserAdmin):
    model = accounts.TeacherUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('teachable_courses','profilepic',)}),
    )


admin.site.register(accounts.AdminUser,AdminUserAdmin)
admin.site.register(accounts.TeacherUser,TeacherUserAdmin)
admin.site.register(accounts.StudentUser,StudentUserAdmin)
admin.site.register(accounts.TempTeacherUser)
admin.site.register(accounts.TempStudentUser)
admin.site.register(education.Batch)
admin.site.register(education.Chapter)
admin.site.register(education.Stream)
admin.site.register(education.Submission)
admin.site.register(education.Assignment)
admin.site.register(education.Course)
admin.site.register(education.Test)
admin.site.register(education.Handout)
admin.site.register(education.Result)
admin.site.register(education.ClassPlan)
admin.site.register(education.Notice)
admin.site.register(education.Notification)

