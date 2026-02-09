from django.contrib import admin
from . import models

admin.site.register(models.Teacher)

admin.site.register(models.CourseCategory)

admin.site.register(models.Course)

admin.site.register(models.Chapter)

admin.site.register(models.Student)

admin.site.register(models.StudentCourseEnrollment)

admin.site.register(models.CourseRating)

admin.site.register(models.StudentFavoriteCourse)

admin.site.register(models.StudyMaterial)

admin.site.register(models.Faq)

admin.site.register(models.SubscriptionPlan)

admin.site.register(models.Subscription)

admin.site.register(models.SubscriptionHistory)

# Teacher Dashboard models
class TeacherStudentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'student', 'instrument', 'level', 'status', 'progress_percentage', 'last_active']
    list_filter = ['status', 'instrument', 'level', 'teacher']
    search_fields = ['teacher__full_name', 'student__fullname', 'student__email']
    raw_id_fields = ['teacher', 'student']

admin.site.register(models.TeacherStudent, TeacherStudentAdmin)
admin.site.register(models.TeacherSession)
admin.site.register(models.TeacherActivity)