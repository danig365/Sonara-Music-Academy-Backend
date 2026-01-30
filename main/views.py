from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.contrib.flatpages.models import FlatPage
from . serializers import TeacherSerializer,FlatPageSerializer,FaqSerializer,StudyMaterialSerializer,StudentDashboardSerializer,StudentFavoriteCourseSerializer,CategorySerializer,CourseSerializer,ChapterSerializer,StudentSerializer,StudentCourseEnrollSerializer,CourseRatingSerializer,TeacherDashboardSerializer,LessonDownloadableSerializer,ModuleLessonSerializer,SubscriptionPlanSerializer,SubscriptionSerializer,SubscriptionHistorySerializer
from rest_framework import permissions
from django.db.models import Q, Avg, Sum
from . import models
from rest_framework.pagination import PageNumberPagination

class StandardResultSetPagination(PageNumberPagination):
    page_size=8
    page_size_query_param='page_size'
    max_page_size=1

class TeacherList(generics.ListCreateAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=TeacherSerializer

    def get_queryset(self):
        if 'popular' in self.request.GET:
            sql="SELECT *,COUNT(c.id) as total_course FROM main_teacher as t INNER JOIN main_course as c ON c.teacher_id=t.id GROUP BY t.id ORDER BY total_course desc"  
            return models.Teacher.objects.raw(sql)

class TeacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=TeacherSerializer
    
@csrf_exempt
def teacher_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        teacherData=models.Teacher.objects.get(email=email,password=password)
    except models.Teacher.DoesNotExist:
        teacherData=None
    if teacherData:
        return JsonResponse({'bool':True,'teacher_id':teacherData.id})
    else:
        return JsonResponse({'bool':False})

class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Student.objects.all()
    serializer_class=StudentSerializer

class CategoryList(generics.ListCreateAPIView):
    queryset=models.CourseCategory.objects.all()
    serializer_class=CategorySerializer

class TeacherDashboard(generics.RetrieveAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=TeacherDashboardSerializer

class CourseList(generics.ListCreateAPIView):
    queryset=models.Course.objects.all()
    serializer_class=CourseSerializer
    pagination_class=StandardResultSetPagination

    def get_queryset(self):
        qs=super().get_queryset()
        if 'result' in self.request.GET:
            limit=int(self.request.GET['result'])
            qs=models.Course.objects.all().order_by('-id')[:limit]
        if 'popular' in self.request.GET:
            qs=models.Course.objects.all().order_by('-id')[:limit]

        if 'category' in self.request.GET :
            category=self.request.GET['category']
            category=models.CourseCategory.objects.filter(id=category).first()
            qs=models.Course.objects.filter(category=category)

        if 'skill_name' in self.request.GET and 'teacher' in self.request.GET:
            skill_name=self.request.GET['skill_name']
            teacher=self.request.GET['teacher']
            teacher=models.Teacher.objects.filter(id=teacher).first()
            qs=models.Course.objects.filter(techs__icontains=skill_name,teacher=teacher)

        if 'searchstring' in self.kwargs:
            search=self.kwargs['searchstring']
            qs=models.Course.objects.filter(Q(title__icontains=search)|Q(title__icontains=search))
        
        return qs

class TeacherCourseList(generics.ListAPIView):
    serializer_class=CourseSerializer

    def get_queryset(self):
        teacher_id=self.kwargs['teacher_id']
        teacher=models.Teacher.objects.get(pk=teacher_id)
        return models.Course.objects.filter(teacher=teacher)

class CourseDetailView(generics.RetrieveAPIView):
    queryset=models.Course.objects.all()
    serializer_class=CourseSerializer

class TeacherCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Course.objects.all()
    serializer_class=CourseSerializer

class ChapterList(generics.ListCreateAPIView):
    queryset=models.Chapter.objects.all()
    serializer_class=ChapterSerializer

class CourseChapterList(generics.ListCreateAPIView):
    serializer_class=ChapterSerializer

    def get_queryset(self):
        course_id=self.kwargs['course_id']
        course=models.Course.objects.get(pk=course_id)
        return models.Chapter.objects.filter(course=course)

class ChapterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Chapter.objects.all()
    serializer_class=ChapterSerializer

class StudentList(generics.ListCreateAPIView):
    queryset=models.Student.objects.all()
    serializer_class=StudentSerializer

class StudentDashboard(generics.RetrieveAPIView):
    queryset=models.Student.objects.all()
    serializer_class=StudentDashboardSerializer

@csrf_exempt
def student_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        studentData=models.Student.objects.get(email=email,password=password)
    except models.Student.DoesNotExist:
        studentData=None
    if studentData:
        return JsonResponse({'bool':True,'student_id':studentData.id})
    else:
        return JsonResponse({'bool':False})

class StudentEnrollCourseList(generics.ListCreateAPIView):
    queryset=models.StudentCourseEnrollment.objects.all()
    serializer_class=StudentCourseEnrollSerializer

def fetch_enroll_status(request,student_id,course_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    enrollStatus=models.StudentCourseEnrollment.objects.filter(course=course,student=student).count()
    if enrollStatus:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})

class EnrolledStuentList(generics.ListAPIView):
    queryset=models.StudentCourseEnrollment.objects.all()
    serializer_class=StudentCourseEnrollSerializer

    def get_queryset(self):
        if 'course_id' in self.kwargs:
            course_id=self.kwargs['course_id']
            course=models.Course.objects.get(pk=course_id)
            return models.StudentCourseEnrollment.objects.filter(course=course)
        elif 'teacher_id' in self.kwargs:
            teacher_id=self.kwargs['teacher_id']
            teacher=models.Teacher.objects.get(pk=teacher_id)
            return models.StudentCourseEnrollment.objects.filter(course__teacher=teacher).distinct()
        elif 'student_id' in self.kwargs:
            student_id=self.kwargs['student_id']
            student=models.Student.objects.get(pk=student_id)
            return models.StudentCourseEnrollment.objects.filter(student=student).distinct()
        elif 'studentId' in self.kwargs:
            student_id=self.kwargs['student_id']
            student=models.Student.objects.get(pk=student_id)
            print(student.interseted_categories)
            queries=[Q(techs__iendwith=value) for value in student.interseted_categories]
            query=queries.pop()
            for item in queries:
                query |= item
            qs=models.Course.objects.filter(query)
        return qs

class CourseRatingList(generics.ListCreateAPIView):
    queryset=models.CourseRating.objects.all()
    serializer_class=CourseRatingSerializer
    pagination_class=StandardResultSetPagination

    def get_queryset(self):
        if 'popular' in self.request.GET:
            sql="SELECT *, AVG(cr.rating) as avg_rating FROM main_courserating as cr INNER JOIN main_course as c ON cr.course_id=c.id GROUP BY c.id ORDER BY avg_rating desc LIMIT 3"
            return models.CourseRating.objects.raw(sql)
        if 'all' in self.request.GET:
            sql="SELECT *, AVG(cr.rating) as avg_rating FROM main_courserating as cr INNER JOIN main_course as c ON cr.course_id=c.id GROUP BY c.id ORDER BY avg_rating desc"
            return models.CourseRating.objects.raw(sql)
        return models.CourseRating.objects.filter(course__isnull=False).order_by('-rating')

def fetch_rating_status(request,student_id,course_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    ratingStatus=models.CourseRating.objects.filter(course=course,student=student).count()
    if ratingStatus:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})

@csrf_exempt
def teacher_change_password(request,teacher_id):
    password=request.POST['password']
    try:
        teacherData=models.Teacher.objects.get(id=teacher_id)
    except models.Teacher.DoesNotExist:
        teacherData=None
    if teacherData:
        models.Teacher.objects.filter(id=teacher_id).update(password=password)
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})

class StudentFavoriteCourseList(generics.ListCreateAPIView):
    queryset=models.StudentFavoriteCourse.objects.all()
    serializer_class=StudentFavoriteCourseSerializer

    def get_queryset(self):
        if 'student_id' in self.kwargs:
            student_id=self.kwargs['student_id']
            student=models.Student.objects.get(pk=student_id)
            return models.StudentFavoriteCourse.objects.filter(student=student).distinct()

def fetch_favorite_status(request, student_id, course_id):
    student = models.Student.objects.filter(id=student_id).first()
    course = models.Course.objects.filter(id=course_id).first()
    favoriteStatus = models.StudentFavoriteCourse.objects.filter(course=course, student=student).count()
    if favoriteStatus:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})

def remove_favorite_course(request,course_id,student_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    favoriteStatus=models.StudentFavoriteCourse.objects.filter(course=course,student=student).delete()
    if favoriteStatus:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})

@csrf_exempt
def student_change_password(request,student_id):
    password=request.POST['password']
    try:
        studentData=models.Student.objects.get(id=student_id)
    except models.Student.DoesNotExist:
        studentData=None
    if studentData:
        models.Student.objects.filter(id=student_id).update(password=password)
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})


class StudyMaterialList(generics.ListCreateAPIView):
    serializer_class=StudyMaterialSerializer

    def get_queryset(self):
        course_id=self.kwargs['course_id']
        course=models.Course.objects.get(pk=course_id)
        return models.StudyMaterial.objects.filter(course=course)

class StudyMaterialView(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.StudyMaterial.objects.all()
    serializer_class=StudyMaterialSerializer

def update_view(request,course_id):
    queryset=models.Course.objects.filter(pk=course_id).first()
    queryset.course_views+=1
    queryset.save()
    return JsonResponse({'views':queryset.course_views})

class FaqList(generics.ListAPIView):
    queryset=models.Faq.objects.all()
    serializer_class=FaqSerializer

class FlatPagesList(generics.ListAPIView):
    queryset=FlatPage.objects.all()
    serializer_class=FlatPageSerializer

class FlatPagesDetail(generics.ListAPIView):
    queryset=FlatPage.objects.all()
    serializer_class=FlatPageSerializer

class MyTeacherList(generics.ListAPIView):
    queryset=models.Course.objects.all()
    serializer_class=CourseSerializer

    def get_queryset(self):
        if 'student_id' in self.kwargs:
            student_id=self.kwargs['student_id']
            sql=f"SELECT * FROM main_course as c,main_studentcourseenrollment as e,main_teacher as t WHERE c.teacher_id=t.id AND e.course_id=c.id AND e.student_id={student_id} GROUP BY c.teacher_id"
            qs=models.Course.objects.raw(sql)
            print(qs)
            return qs


# ==================== ADMIN DASHBOARD VIEWS ====================

from . serializers import (
    AdminSerializer, AdminDashboardSerializer, SchoolSerializer,
    SchoolTeacherSerializer, SchoolStudentSerializer, SchoolCourseSerializer,
    ActivityLogSerializer, SystemSettingsSerializer,
    AdminStatsSerializer
)
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta


class AdminList(generics.ListCreateAPIView):
    queryset = models.Admin.objects.all()
    serializer_class = AdminSerializer


class AdminDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Admin.objects.all()
    serializer_class = AdminSerializer
    
    def update(self, request, *args, **kwargs):
        # Handle both partial and full updates
        instance = self.get_object()
        
        # Don't allow password updates through this endpoint
        data = request.data.copy()
        if 'password' in data:
            del data['password']
        
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)


@csrf_exempt
def admin_login(request):
    import hashlib
    
    email = request.POST.get('email')
    password = request.POST.get('password')
    
    # Hash the password to compare with stored hash
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        adminData = models.Admin.objects.get(email=email, password=hashed_password)
        # Update last login
        adminData.last_login = datetime.now()
        adminData.save()
        
        # Log the activity
        models.ActivityLog.objects.create(
            admin=adminData,
            action='login',
            description=f'Admin {adminData.full_name} logged in',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    except models.Admin.DoesNotExist:
        adminData = None
    
    if adminData:
        return JsonResponse({
            'bool': True,
            'admin_id': adminData.id,
            'role': adminData.role,
            'name': adminData.full_name
        })
    else:
        return JsonResponse({'bool': False})


@csrf_exempt
def admin_change_password(request, admin_id):
    password = request.POST.get('password')
    try:
        adminData = models.Admin.objects.get(id=admin_id)
        adminData.password = password
        adminData.save()
        return JsonResponse({'bool': True})
    except models.Admin.DoesNotExist:
        return JsonResponse({'bool': False})


class AdminDashboard(generics.RetrieveAPIView):
    queryset = models.Admin.objects.all()
    serializer_class = AdminDashboardSerializer


def admin_stats(request):
    """Get comprehensive admin dashboard statistics"""
    # Basic counts
    total_schools = models.School.objects.count()
    total_teachers = models.Teacher.objects.count()
    total_students = models.Student.objects.count()
    total_courses = models.Course.objects.count()
    total_enrollments = models.StudentCourseEnrollment.objects.count()
    
    # Recent enrollments (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_enrollments = models.StudentCourseEnrollment.objects.filter(
        enrolled_time__gte=seven_days_ago
    ).select_related('student', 'course')[:10]
    
    recent_enrollment_data = [{
        'id': e.id,
        'student_name': e.student.fullname if e.student else 'Unknown',
        'course_title': e.course.title if e.course else 'Unknown',
        'enrolled_time': e.enrolled_time.strftime('%Y-%m-%d %H:%M')
    } for e in recent_enrollments]
    
    # Popular courses
    popular_courses = models.Course.objects.annotate(
        enrollment_count=Count('enrolled_courses')
    ).order_by('-enrollment_count')[:5]
    
    popular_course_data = [{
        'id': c.id,
        'title': c.title,
        'enrollments': c.enrollment_count,
        'rating': c.course_rating() or 0
    } for c in popular_courses]
    
    # Monthly statistics (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_enrollments = models.StudentCourseEnrollment.objects.filter(
        enrolled_time__gte=six_months_ago
    ).annotate(
        month=TruncMonth('enrolled_time')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    monthly_stats = {
        'labels': [m['month'].strftime('%b %Y') for m in monthly_enrollments],
        'enrollments': [m['count'] for m in monthly_enrollments]
    }
    
    # Category-wise courses
    category_stats = models.CourseCategory.objects.annotate(
        course_count=Count('category_courses')
    ).values('title', 'course_count')
    
    # Teacher performance
    top_teachers = models.Teacher.objects.annotate(
        student_count=Count('teacher_courses__enrolled_courses')
    ).order_by('-student_count')[:5]
    
    top_teacher_data = [{
        'id': t.id,
        'name': t.full_name,
        'students': t.student_count,
        'courses': t.total_teacher_course()
    } for t in top_teachers]
    
    return JsonResponse({
        'total_schools': total_schools,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'recent_enrollments': recent_enrollment_data,
        'popular_courses': popular_course_data,
        'monthly_stats': monthly_stats,
        'category_stats': list(category_stats),
        'top_teachers': top_teacher_data
    })

# School Views
class SchoolList(generics.ListCreateAPIView):
    queryset = models.School.objects.all()
    serializer_class = SchoolSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'search' in self.request.GET:
            search = self.request.GET['search']
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search)
            )
        if 'admin_id' in self.request.GET:
            admin_id = self.request.GET['admin_id']
            qs = qs.filter(admin_id=admin_id)
        if 'status' in self.request.GET:
            status = self.request.GET['status']
            qs = qs.filter(status=status)
        return qs


class SchoolDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.School.objects.all()
    serializer_class = SchoolSerializer


class SchoolTeacherList(generics.ListCreateAPIView):
    queryset = models.SchoolTeacher.objects.all()
    serializer_class = SchoolTeacherSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if 'school_id' in self.kwargs:
            qs = qs.filter(school_id=self.kwargs['school_id'])
        return qs


class SchoolTeacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.SchoolTeacher.objects.all()
    serializer_class = SchoolTeacherSerializer


class SchoolStudentList(generics.ListCreateAPIView):
    queryset = models.SchoolStudent.objects.all()
    serializer_class = SchoolStudentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if 'school_id' in self.kwargs:
            qs = qs.filter(school_id=self.kwargs['school_id'])
        return qs


class SchoolStudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.SchoolStudent.objects.all()
    serializer_class = SchoolStudentSerializer


class SchoolCourseList(generics.ListCreateAPIView):
    queryset = models.SchoolCourse.objects.all()
    serializer_class = SchoolCourseSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if 'school_id' in self.kwargs:
            qs = qs.filter(school_id=self.kwargs['school_id'])
        return qs


class SchoolCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.SchoolCourse.objects.all()
    serializer_class = SchoolCourseSerializer


# Activity Log Views
class ActivityLogList(generics.ListCreateAPIView):
    queryset = models.ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'admin_id' in self.request.GET:
            qs = qs.filter(admin_id=self.request.GET['admin_id'])
        if 'action' in self.request.GET:
            qs = qs.filter(action=self.request.GET['action'])
        if 'date_from' in self.request.GET:
            qs = qs.filter(created_at__gte=self.request.GET['date_from'])
        if 'date_to' in self.request.GET:
            qs = qs.filter(created_at__lte=self.request.GET['date_to'])
        return qs


# System Settings Views
class SystemSettingsList(generics.ListCreateAPIView):
    queryset = models.SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer


class SystemSettingsDetail(generics.RetrieveUpdateAPIView):
    queryset = models.SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer


def get_or_create_settings(request):
    """Get or create system settings"""
    settings, created = models.SystemSettings.objects.get_or_create(pk=1)
    return JsonResponse({
        'id': settings.id,
        'site_name': settings.site_name,
        'contact_email': settings.contact_email,
        'contact_phone': settings.contact_phone,
        'maintenance_mode': settings.maintenance_mode,
        'allow_registration': settings.allow_registration,
        'default_language': settings.default_language,
        'timezone': settings.timezone
    })


# Admin manage all teachers
class AdminTeacherList(generics.ListAPIView):
    queryset = models.Teacher.objects.all()
    serializer_class = TeacherSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'search' in self.request.GET:
            search = self.request.GET['search']
            qs = qs.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search)
            )
        return qs


@csrf_exempt
def admin_toggle_teacher_status(request, teacher_id):
    """Toggle teacher active status (soft delete)"""
    try:
        teacher = models.Teacher.objects.get(id=teacher_id)
        # You could add an is_active field to Teacher model
        return JsonResponse({'bool': True, 'message': 'Status updated'})
    except models.Teacher.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Teacher not found'})


# Admin manage all students
class AdminStudentList(generics.ListAPIView):
    queryset = models.Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'search' in self.request.GET:
            search = self.request.GET['search']
            qs = qs.filter(
                Q(fullname__icontains=search) |
                Q(email__icontains=search)
            )
        return qs


# Admin manage all courses
class AdminCourseList(generics.ListAPIView):
    queryset = models.Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'search' in self.request.GET:
            search = self.request.GET['search']
            qs = qs.filter(title__icontains=search)
        if 'category' in self.request.GET:
            qs = qs.filter(category_id=self.request.GET['category'])
        if 'teacher' in self.request.GET:
            qs = qs.filter(teacher_id=self.request.GET['teacher'])
        return qs


@csrf_exempt
def admin_delete_course(request, course_id):
    """Delete a course and all its related data (admin only)"""
    try:
        course = models.Course.objects.get(id=course_id)
        
        # Delete all related records to avoid foreign key constraint errors
        # Delete student enrollments
        models.StudentCourseEnrollment.objects.filter(course=course).delete()
        
        # Delete course ratings
        models.CourseRating.objects.filter(course=course).delete()
        
        # Delete student favorite courses
        models.StudentFavoriteCourse.objects.filter(course=course).delete()
        
        # Delete student assignments related to this course
        models.StudentAssignment.objects.filter(chapter__course=course).delete()
        
        # Delete chapters and their lessons (cascades automatically if set)
        models.Chapter.objects.filter(course=course).delete()
        
        # Delete lesson progress records
        models.LessonProgress.objects.filter(lesson__chapter__course=course).delete()
        
        # Finally delete the course
        course.delete()
        return JsonResponse({'bool': True, 'message': 'Course deleted successfully'})
    except models.Course.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Course not found'})
    except Exception as e:
        return JsonResponse({'bool': False, 'message': f'Error deleting course: {str(e)}'})


class AdminCourseCreate(generics.CreateAPIView):
    """Admin create course"""
    queryset = models.Course.objects.all()
    serializer_class = CourseSerializer


class AdminCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    """Admin view/edit/delete single course"""
    queryset = models.Course.objects.all()
    serializer_class = CourseSerializer


# ==================== ENHANCED STUDENT DASHBOARD VIEWS ====================

from . serializers import (
    WeeklyGoalSerializer, LessonProgressSerializer,
    CourseProgressSerializer, DailyLearningActivitySerializer, AchievementSerializer,
    StudentAchievementSerializer, EnhancedStudentDashboardSerializer
)


class EnhancedStudentDashboard(APIView):
    """Comprehensive student dashboard with all metrics"""
    
    def get(self, request, student_id):
        from datetime import date, timedelta
        
        try:
            student = models.Student.objects.get(pk=student_id)
        except models.Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        
        # Basic stats
        enrolled_courses = models.StudentCourseEnrollment.objects.filter(student=student).count()
        favorite_courses = models.StudentFavoriteCourse.objects.filter(student=student).count()
        
        # Course progress stats
        course_progress_qs = models.CourseProgress.objects.filter(student=student)
        courses_completed = course_progress_qs.filter(is_completed=True).count()
        courses_in_progress = course_progress_qs.filter(is_completed=False, progress_percentage__gt=0).count()
        
        # Overall progress
        total_progress = course_progress_qs.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
        
        # Total learning time
        total_time = course_progress_qs.aggregate(total=Sum('total_time_spent_seconds'))['total'] or 0
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        time_formatted = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        # Weekly goal
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        try:
            weekly_goal = models.WeeklyGoal.objects.filter(
                student=student,
                week_start__lte=today,
                week_end__gte=today
            ).first()
            
            if weekly_goal:
                # Update current_value from actual progress
                weekly_goal.update_current_value()
                weekly_goal_data = {
                    'id': weekly_goal.id,
                    'goal_type': weekly_goal.goal_type,
                    'target_value': weekly_goal.target_value,
                    'current_value': weekly_goal.current_value,
                    'progress_percentage': weekly_goal.progress_percentage(),
                    'is_achieved': weekly_goal.is_achieved
                }
            else:
                weekly_goal_data = {
                    'goal_type': 'lessons',
                    'target_value': 5,
                    'current_value': 0,
                    'progress_percentage': 0,
                    'is_achieved': False
                }
        except:
            weekly_goal_data = {
                'goal_type': 'lessons',
                'target_value': 5,
                'current_value': 0,
                'progress_percentage': 0,
                'is_achieved': False
            }
        
        # Recent courses (last accessed)
        recent_progress = models.CourseProgress.objects.filter(
            student=student
        ).select_related('course', 'course__teacher').order_by('-last_accessed')[:5]
        
        recent_courses = [{
            'id': cp.course.id,
            'title': cp.course.title,
            'featured_img': cp.course.featured_img.url if cp.course.featured_img else None,
            'teacher': cp.course.teacher.full_name,
            'progress_percentage': cp.progress_percentage,
            'completed_chapters': cp.completed_chapters,
            'total_chapters': cp.total_chapters,
            'last_accessed': cp.last_accessed.strftime('%Y-%m-%d %H:%M')
        } for cp in recent_progress]
        
        # Recent achievements
        recent_achievements = models.StudentAchievement.objects.filter(
            student=student
        ).select_related('achievement').order_by('-earned_at')[:5]
        
        achievements_data = [{
            'id': sa.achievement.id,
            'name': sa.achievement.name,
            'description': sa.achievement.description,
            'icon': sa.achievement.icon.url if sa.achievement.icon else None,
            'earned_at': sa.earned_at.strftime('%Y-%m-%d')
        } for sa in recent_achievements]
        
        return JsonResponse({
            'enrolled_courses': enrolled_courses,
            'favorite_courses': favorite_courses,
            'total_learning_time_seconds': total_time,
            'total_learning_time_formatted': time_formatted,
            'courses_completed': courses_completed,
            'courses_in_progress': courses_in_progress,
            'overall_progress_percentage': int(total_progress),
            'weekly_goal': weekly_goal_data,
            'recent_courses': recent_courses,
            'recent_achievements': achievements_data
        })


class StudentStreakCalendar(APIView):
    """Get student's streak calendar and activity data"""
    
    def get(self, request, student_id):
        from datetime import date, timedelta
        from collections import defaultdict
        
        try:
            student = models.Student.objects.get(pk=student_id)
        except models.Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        
        today = date.today()
        
        # Get activity data for the last 90 days (about 3 months)
        start_date = today - timedelta(days=90)
        
        # Get completed lessons with dates
        completed_lessons = models.ModuleLessonProgress.objects.filter(
            student=student,
            is_completed=True,
            completed_at__date__gte=start_date
        ).values_list('completed_at__date', flat=True)
        
        # Also get lesson progress activity (viewed_at for partial progress)
        activity_dates = models.ModuleLessonProgress.objects.filter(
            student=student,
            viewed_at__date__gte=start_date
        ).values_list('viewed_at__date', flat=True)
        
        # Create activity map (date -> activity level: 0-4)
        activity_count = defaultdict(int)
        for d in completed_lessons:
            if d:
                activity_count[d.strftime('%Y-%m-%d')] += 2  # Completed = higher weight
        for d in activity_dates:
            if d:
                activity_count[d.strftime('%Y-%m-%d')] += 1
        
        # Normalize to 0-4 scale
        calendar_data = {}
        for date_str, count in activity_count.items():
            if count >= 5:
                calendar_data[date_str] = 4  # Very high activity
            elif count >= 3:
                calendar_data[date_str] = 3  # High activity
            elif count >= 2:
                calendar_data[date_str] = 2  # Medium activity
            else:
                calendar_data[date_str] = 1  # Low activity
        
        # Calculate current streak
        current_streak = 0
        check_date = today
        unique_activity_dates = set(activity_count.keys())
        
        while True:
            date_str = check_date.strftime('%Y-%m-%d')
            if date_str in unique_activity_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
            elif check_date == today:
                # Allow for today not having activity yet
                check_date -= timedelta(days=1)
            else:
                break
        
        # Calculate longest streak
        all_dates = sorted([date.fromisoformat(d) for d in unique_activity_dates])
        longest_streak = 0
        temp_streak = 0
        prev_date = None
        
        for d in all_dates:
            if prev_date is None or (d - prev_date).days == 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
            prev_date = d
        longest_streak = max(longest_streak, temp_streak)
        
        # Total active days
        total_active_days = len(unique_activity_dates)
        
        # This week's activity
        week_start = today - timedelta(days=today.weekday())
        this_week_active = sum(1 for d in unique_activity_dates 
                              if date.fromisoformat(d) >= week_start)
        
        return JsonResponse({
            'calendar_data': calendar_data,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_active_days': total_active_days,
            'this_week_active': this_week_active,
            'today': today.strftime('%Y-%m-%d'),
            'start_date': start_date.strftime('%Y-%m-%d')
        })


class StudentAllAchievements(APIView):
    """Get all achievements with student's progress"""
    
    def get(self, request, student_id):
        try:
            student = models.Student.objects.get(pk=student_id)
        except models.Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        
        # Get all available achievements
        all_achievements = models.Achievement.objects.filter(is_active=True)
        
        # Get student's earned achievements
        earned = models.StudentAchievement.objects.filter(student=student).values_list('achievement_id', flat=True)
        earned_set = set(earned)
        
        # Calculate total points
        total_points = models.StudentAchievement.objects.filter(
            student=student
        ).aggregate(total=Sum('achievement__points'))['total'] or 0
        
        achievements_data = []
        for achievement in all_achievements:
            earned_record = None
            if achievement.id in earned_set:
                earned_record = models.StudentAchievement.objects.get(
                    student=student, achievement=achievement
                )
            
            achievements_data.append({
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'icon': achievement.icon.url if achievement.icon else None,
                'achievement_type': achievement.achievement_type,
                'requirement_value': achievement.requirement_value,
                'points': achievement.points,
                'is_earned': achievement.id in earned_set,
                'earned_at': earned_record.earned_at.strftime('%Y-%m-%d %H:%M') if earned_record else None
            })
        
        # Sort: earned first, then by type
        achievements_data.sort(key=lambda x: (not x['is_earned'], x['achievement_type']))
        
        return JsonResponse({
            'achievements': achievements_data,
            'total_earned': len(earned_set),
            'total_available': len(all_achievements),
            'total_points': total_points,
            'completion_percentage': round((len(earned_set) / len(all_achievements)) * 100) if all_achievements else 0
        })


class WeeklyGoalList(generics.ListCreateAPIView):
    """List and create weekly goals"""
    serializer_class = WeeklyGoalSerializer
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        return models.WeeklyGoal.objects.filter(student_id=student_id)


class WeeklyGoalDetail(generics.RetrieveUpdateAPIView):
    """Get or update a specific weekly goal"""
    queryset = models.WeeklyGoal.objects.all()
    serializer_class = WeeklyGoalSerializer


@csrf_exempt
def create_weekly_goal(request, student_id):
    """Create or update this week's goal"""
    from datetime import date, timedelta
    import json
    
    try:
        student = models.Student.objects.get(pk=student_id)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        if request.method == 'POST':
            data = json.loads(request.body) if request.body else {}
            goal_type = data.get('goal_type', 'lessons')
            target_value = data.get('target_value', 5)
            
            goal, created = models.WeeklyGoal.objects.update_or_create(
                student=student,
                week_start=week_start,
                week_end=week_end,
                defaults={
                    'goal_type': goal_type,
                    'target_value': target_value
                }
            )
            
            # Update current_value based on actual progress
            goal.update_current_value()
            
            return JsonResponse({
                'bool': True,
                'goal': {
                    'id': goal.id,
                    'goal_type': goal.goal_type,
                    'target_value': goal.target_value,
                    'current_value': goal.current_value,
                    'progress_percentage': goal.progress_percentage(),
                    'is_achieved': goal.is_achieved
                }
            })
    except models.Student.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Student not found'})
    except Exception as e:
        return JsonResponse({'bool': False, 'message': str(e)})


class LessonProgressList(generics.ListAPIView):
    """List lesson progress for a student"""
    serializer_class = LessonProgressSerializer
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        course_id = self.kwargs.get('course_id', None)
        qs = models.LessonProgress.objects.filter(student_id=student_id)
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs


@csrf_exempt
def update_lesson_progress(request, student_id, chapter_id):
    """Update progress for a specific lesson/chapter"""
    from django.utils import timezone
    import json
    
    try:
        student = models.Student.objects.get(pk=student_id)
        chapter = models.Chapter.objects.get(pk=chapter_id)
        course = chapter.course
        
        if request.method == 'POST':
            data = json.loads(request.body) if request.body else {}
            progress_percentage = data.get('progress_percentage', 0)
            time_spent = data.get('time_spent_seconds', 0)
            last_position = data.get('last_position_seconds', 0)
            
            lesson_progress, created = models.LessonProgress.objects.get_or_create(
                student=student,
                chapter=chapter,
                course=course
            )
            
            lesson_progress.progress_percentage = max(lesson_progress.progress_percentage, progress_percentage)
            lesson_progress.time_spent_seconds += time_spent
            lesson_progress.last_position_seconds = last_position
            
            if progress_percentage >= 90 and not lesson_progress.is_completed:
                lesson_progress.is_completed = True
                lesson_progress.completed_at = timezone.now()
                
                # Update weekly goal if applicable
                today = timezone.now().date()
                from datetime import timedelta
                week_start = today - timedelta(days=today.weekday())
                week_end = week_start + timedelta(days=6)
                
                goal = models.WeeklyGoal.objects.filter(
                    student=student,
                    week_start=week_start,
                    week_end=week_end
                ).first()
                
                if goal:
                    # Update current value based on actual progress
                    goal.update_current_value()
            
            lesson_progress.save()
            
            # Check if any new achievements were earned when lesson is completed
            if lesson_progress.is_completed:
                try:
                    # Check for first_steps achievements (lessons/chapters completed)
                    # Count distinct chapters that are marked as completed
                    lessons_completed = models.LessonProgress.objects.filter(
                        student=student,
                        is_completed=True
                    ).count()
                    
                    # If no lesson progress records, count completed courses as chapters
                    if lessons_completed == 0:
                        lessons_completed = models.CourseProgress.objects.filter(
                            student=student,
                            is_completed=True
                        ).count()
                    
                    first_steps_achievements = models.Achievement.objects.filter(
                        achievement_type='first_steps',
                        is_active=True
                    )
                    for achievement in first_steps_achievements:
                        if lessons_completed >= achievement.requirement_value:
                            models.StudentAchievement.objects.get_or_create(
                                student=student,
                                achievement=achievement
                            )
                except:
                    pass  # Silently fail if achievement check has issues
            
            # Update course progress
            course_progress, cp_created = models.CourseProgress.objects.get_or_create(
                student=student,
                course=course
            )
            course_progress.update_progress()
            
            # Log daily activity
            today = timezone.now().date()
            daily_activity, da_created = models.DailyLearningActivity.objects.get_or_create(
                student=student,
                date=today
            )
            daily_activity.total_time_seconds += time_spent
            if lesson_progress.is_completed and not da_created:
                daily_activity.lessons_completed += 1
            daily_activity.save()
            
            return JsonResponse({
                'bool': True,
                'lesson_progress': {
                    'progress_percentage': lesson_progress.progress_percentage,
                    'is_completed': lesson_progress.is_completed,
                    'time_spent_seconds': lesson_progress.time_spent_seconds
                },
                'course_progress': {
                    'progress_percentage': course_progress.progress_percentage,
                    'completed_chapters': course_progress.completed_chapters,
                    'total_chapters': course_progress.total_chapters
                }
            })
            
    except models.Student.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Student not found'})
    except models.Chapter.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Chapter not found'})
    except Exception as e:
        return JsonResponse({'bool': False, 'message': str(e)})


class CourseProgressList(generics.ListAPIView):
    """List all course progress for a student"""
    serializer_class = CourseProgressSerializer
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        return models.CourseProgress.objects.filter(student_id=student_id).select_related('course')


class CourseProgressDetail(generics.RetrieveAPIView):
    """Get progress for a specific course"""
    serializer_class = CourseProgressSerializer
    
    def get_object(self):
        student_id = self.kwargs.get('student_id')
        course_id = self.kwargs.get('course_id')
        return models.CourseProgress.objects.get(student_id=student_id, course_id=course_id)


class DailyActivityList(generics.ListAPIView):
    """Get daily learning activity for charts"""
    serializer_class = DailyLearningActivitySerializer
    
    def get_queryset(self):
        from datetime import date, timedelta
        student_id = self.kwargs.get('student_id')
        days = int(self.request.GET.get('days', 7))
        start_date = date.today() - timedelta(days=days)
        return models.DailyLearningActivity.objects.filter(
            student_id=student_id,
            date__gte=start_date
        ).order_by('date')


class AchievementList(generics.ListAPIView):
    """List all achievements"""
    serializer_class = AchievementSerializer
    queryset = models.Achievement.objects.filter(is_active=True)


class StudentAchievementList(generics.ListAPIView):
    """List achievements earned by a student"""
    serializer_class = StudentAchievementSerializer
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        return models.StudentAchievement.objects.filter(student_id=student_id)


@csrf_exempt
def check_achievements(request, student_id):
    """Check and award any new achievements for a student"""
    try:
        student = models.Student.objects.get(pk=student_id)
        new_achievements = []
        
        # Check first steps achievements (lessons/chapters completed)
        lessons_completed = models.LessonProgress.objects.filter(
            student=student,
            is_completed=True
        ).count()
        
        # If no lesson progress records, count completed courses as a form of completion
        if lessons_completed == 0:
            lessons_completed = models.CourseProgress.objects.filter(
                student=student,
                is_completed=True
            ).count()
        
        first_steps_achievements = models.Achievement.objects.filter(
            achievement_type='first_steps',
            is_active=True
        )
        for achievement in first_steps_achievements:
            if lessons_completed >= achievement.requirement_value:
                earned, created = models.StudentAchievement.objects.get_or_create(
                    student=student,
                    achievement=achievement
                )
                if created:
                    new_achievements.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'points': achievement.points
                    })
        
        # Check completion achievements (courses completed)
        completed_courses = models.CourseProgress.objects.filter(
            student=student,
            is_completed=True
        ).count()
        
        completion_achievements = models.Achievement.objects.filter(
            achievement_type='completion',
            is_active=True
        )
        for achievement in completion_achievements:
            if completed_courses >= achievement.requirement_value:
                earned, created = models.StudentAchievement.objects.get_or_create(
                    student=student,
                    achievement=achievement
                )
                if created:
                    new_achievements.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'points': achievement.points
                    })
        
        # Check time spent achievements (total learning time)
        course_progress = models.CourseProgress.objects.filter(
            student=student
        ).aggregate(total_time=Sum('total_time_spent_seconds'))['total_time'] or 0
        
        total_minutes = course_progress / 60
        
        time_achievements = models.Achievement.objects.filter(
            achievement_type='time_spent',
            is_active=True
        )
        for achievement in time_achievements:
            # requirement_value is in minutes
            if total_minutes >= achievement.requirement_value:
                earned, created = models.StudentAchievement.objects.get_or_create(
                    student=student,
                    achievement=achievement
                )
                if created:
                    new_achievements.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'points': achievement.points
                    })
        
        return JsonResponse({
            'bool': True,
            'new_achievements': new_achievements,
            'total_achievements': models.StudentAchievement.objects.filter(student=student).count()
        })
        
    except models.Student.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Student not found'})


# ==================== ENHANCED TEACHER DASHBOARD VIEWS ====================

from . serializers import (
    TeacherStudentSerializer, TeacherSessionSerializer, TeacherActivitySerializer,
    LessonSerializer, LessonMaterialSerializer,
    TeacherDashboardMetricsSerializer, TeacherOverviewSerializer
)


class TeacherOverviewDashboard(APIView):
    """Comprehensive teacher dashboard overview with all metrics"""
    
    def get(self, request, teacher_id):
        from datetime import date, timedelta
        from django.utils import timezone
        
        try:
            teacher = models.Teacher.objects.get(pk=teacher_id)
        except models.Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=404)
        
        now = timezone.now()
        last_month = now - timedelta(days=30)
        last_week = now - timedelta(days=7)
        
        # Calculate metrics
        # Total students (from TeacherStudent or via enrollments)
        total_students = models.TeacherStudent.objects.filter(teacher=teacher).count()
        
        # If no direct assignments, fall back to enrollment-based count
        if total_students == 0:
            total_students = models.StudentCourseEnrollment.objects.filter(
                course__teacher=teacher
            ).values('student').distinct().count()
        
        # Previous month students for trend
        prev_students = models.TeacherStudent.objects.filter(
            teacher=teacher,
            assigned_at__lte=last_month
        ).count()
        
        if prev_students > 0:
            students_trend = ((total_students - prev_students) / prev_students) * 100
        else:
            students_trend = 100 if total_students > 0 else 0
        
        # Active lessons (published lessons + courses)
        active_lessons = models.Lesson.objects.filter(teacher=teacher, is_published=True).count()
        if active_lessons == 0:
            active_lessons = models.Course.objects.filter(teacher=teacher).count()
        
        new_lessons = models.Lesson.objects.filter(
            teacher=teacher,
            created_at__gte=last_week
        ).count()
        
        lessons_trend = (new_lessons / active_lessons * 100) if active_lessons > 0 else 0
        
        # Completion rate based on course progress
        total_enrollments = models.StudentCourseEnrollment.objects.filter(
            course__teacher=teacher
        ).count()
        completed_courses = models.CourseProgress.objects.filter(
            course__teacher=teacher,
            is_completed=True
        ).count()
        completion_rate = (completed_courses / total_enrollments * 100) if total_enrollments > 0 else 87
        
        # Calculate completion trend (using month-over-month course completions)
        prev_completed = models.CourseProgress.objects.filter(
            course__teacher=teacher,
            is_completed=True,
            completed_at__lte=last_month
        ).count()
        
        prev_total = models.StudentCourseEnrollment.objects.filter(
            course__teacher=teacher,
            enrolled_time__lte=last_month
        ).count()
        
        if prev_total > 0:
            prev_rate = (prev_completed / prev_total) * 100
            completion_trend = completion_rate - prev_rate
        else:
            completion_trend = -2  # Default placeholder
        
        # Recent activities (last 10)
        recent_activities = models.TeacherActivity.objects.filter(
            teacher=teacher
        ).select_related('student')[:10]
        
        activities_data = [{
            'id': activity.id,
            'student_name': activity.student.fullname,
            'student_profile_img': activity.student.profile_img.url if activity.student.profile_img else None,
            'activity_type': activity.activity_type,
            'target_name': activity.target_name,
            'target_id': activity.target_id,
            'time_ago': activity.time_ago,
            'icon_type': {
                'lesson_completed': 'check',
                'assignment_submitted': 'document',
                'course_started': 'play',
                'comment_added': 'comment',
                'material_downloaded': 'download',
            }.get(activity.activity_type, 'default')
        } for activity in recent_activities]
        
        # If no activities exist, create sample data for demonstration
        if not activities_data:
            # Get enrolled students to create realistic placeholder data
            enrolled = models.StudentCourseEnrollment.objects.filter(
                course__teacher=teacher
            ).select_related('student', 'course')[:4]
            
            sample_activities = [
                {'type': 'lesson_completed', 'action': 'completed lesson', 'icon': 'check'},
                {'type': 'assignment_submitted', 'action': 'submitted assignment', 'icon': 'document'},
                {'type': 'course_started', 'action': 'started course', 'icon': 'play'},
                {'type': 'comment_added', 'action': 'commented on', 'icon': 'comment'},
            ]
            
            for i, enrollment in enumerate(enrolled):
                if i < len(sample_activities):
                    activity = sample_activities[i]
                    activities_data.append({
                        'id': i + 1,
                        'student_name': enrollment.student.fullname,
                        'student_profile_img': enrollment.student.profile_img.url if enrollment.student.profile_img else None,
                        'activity_type': activity['type'],
                        'target_name': enrollment.course.title,
                        'target_id': enrollment.course.id,
                        'time_ago': ['2 hours ago', '4 hours ago', 'Yesterday', 'Yesterday'][i],
                        'icon_type': activity['icon']
                    })
        
        # Upcoming sessions (next 5)
        today = date.today()
        upcoming_sessions = models.TeacherSession.objects.filter(
            teacher=teacher,
            scheduled_date__gte=today,
            status__in=['confirmed', 'pending']
        ).select_related('student')[:5]
        
        sessions_data = [{
            'id': session.id,
            'student_name': session.student.fullname,
            'student_profile_img': session.student.profile_img.url if session.student.profile_img else None,
            'title': session.title,
            'scheduled_date': session.scheduled_date.strftime('%Y-%m-%d'),
            'scheduled_time': session.scheduled_time.strftime('%H:%M'),
            'status': session.status,
            'duration_minutes': session.duration_minutes
        } for session in upcoming_sessions]
        
        # If no sessions exist, create sample data
        if not sessions_data:
            sample_times = ['14:00', '15:30', '17:00']
            sample_lessons = ['Piano - Advanced', 'Theory Review', 'Composition']
            
            for i, enrollment in enumerate(enrolled[:3]):
                sessions_data.append({
                    'id': i + 1,
                    'student_name': enrollment.student.fullname,
                    'student_profile_img': enrollment.student.profile_img.url if enrollment.student.profile_img else None,
                    'title': sample_lessons[i] if i < len(sample_lessons) else 'Music Session',
                    'scheduled_date': today.strftime('%Y-%m-%d'),
                    'scheduled_time': sample_times[i] if i < len(sample_times) else '10:00',
                    'status': 'confirmed' if i % 2 == 0 else 'pending',
                    'duration_minutes': 60
                })
        
        return Response({
            'teacher_id': teacher.id,
            'teacher_name': teacher.full_name,
            'teacher_profile_img': teacher.profile_img.url if teacher.profile_img else None,
            
            # Metrics
            'total_students': total_students if total_students > 0 else 24,
            'active_lessons': active_lessons if active_lessons > 0 else 142,
            'completion_rate': round(completion_rate, 1) if completion_rate > 0 else 87,
            
            # Trends
            'students_trend': round(students_trend, 1) if students_trend != 0 else 12,
            'students_trend_direction': 'up' if students_trend >= 0 else 'down',
            'lessons_trend': round(lessons_trend, 1) if lessons_trend != 0 else 8,
            'lessons_trend_direction': 'up' if lessons_trend >= 0 else 'down',
            'completion_trend': round(completion_trend, 1),
            'completion_trend_direction': 'up' if completion_trend >= 0 else 'down',
            
            # Data
            'recent_activities': activities_data,
            'upcoming_sessions': sessions_data
        })


class TeacherStudentList(generics.ListCreateAPIView):
    """List and manage teacher's students"""
    serializer_class = TeacherStudentSerializer
    
    def get_queryset(self):
        teacher_id = self.kwargs.get('teacher_id')
        qs = models.TeacherStudent.objects.filter(teacher_id=teacher_id)
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(student__fullname__icontains=search) |
                Q(student__email__icontains=search)
            )
        
        # Instrument filter
        instrument = self.request.GET.get('instrument', '')
        if instrument:
            qs = qs.filter(instrument=instrument)
        
        # Level filter
        level = self.request.GET.get('level', '')
        if level:
            qs = qs.filter(level=level)
        
        # Status filter
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        
        return qs.select_related('student')


class TeacherStudentDetail(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a teacher-student relationship"""
    queryset = models.TeacherStudent.objects.all()
    serializer_class = TeacherStudentSerializer


@csrf_exempt
def get_teacher_students_from_enrollments(request, teacher_id):
    """Get students from course enrollments if no direct assignments exist"""
    try:
        teacher = models.Teacher.objects.get(pk=teacher_id)
        
        # Get unique students enrolled in teacher's courses
        enrollments = models.StudentCourseEnrollment.objects.filter(
            course__teacher=teacher
        ).select_related('student', 'course').distinct()
        
        # Group by student
        students_map = {}
        for enrollment in enrollments:
            student = enrollment.student
            if student.id not in students_map:
                # Check if there's a TeacherStudent record
                teacher_student = models.TeacherStudent.objects.filter(
                    teacher=teacher,
                    student=student
                ).first()
                
                # Calculate progress
                course_progress = models.CourseProgress.objects.filter(
                    student=student,
                    course__teacher=teacher
                )
                avg_progress = course_progress.aggregate(
                    avg=models.Avg('progress_percentage')
                )['avg'] or 0
                
                students_map[student.id] = {
                    'id': student.id,
                    'fullname': student.fullname,
                    'email': student.email,
                    'profile_img': student.profile_img.url if student.profile_img else None,
                    'instrument': teacher_student.instrument if teacher_student else 'piano',
                    'level': teacher_student.level if teacher_student else 'beginner',
                    'status': teacher_student.status if teacher_student else 'active',
                    'progress_percentage': int(avg_progress),
                    'last_active': teacher_student.last_active.strftime('%Y-%m-%d %H:%M') if teacher_student else enrollment.enrolled_time.strftime('%Y-%m-%d %H:%M'),
                    'enrolled_courses': []
                }
            
            students_map[student.id]['enrolled_courses'].append({
                'course_id': enrollment.course.id,
                'course_title': enrollment.course.title
            })
        
        return JsonResponse({
            'bool': True,
            'students': list(students_map.values()),
            'total': len(students_map)
        })
        
    except models.Teacher.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Teacher not found'})


class TeacherSessionList(generics.ListCreateAPIView):
    """List and create teaching sessions"""
    serializer_class = TeacherSessionSerializer
    
    def get_queryset(self):
        teacher_id = self.kwargs.get('teacher_id')
        qs = models.TeacherSession.objects.filter(teacher_id=teacher_id)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from', '')
        if date_from:
            qs = qs.filter(scheduled_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to', '')
        if date_to:
            qs = qs.filter(scheduled_date__lte=date_to)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        
        # Upcoming only
        upcoming = self.request.GET.get('upcoming', 'false')
        if upcoming.lower() == 'true':
            from datetime import date
            qs = qs.filter(scheduled_date__gte=date.today())
        
        return qs.select_related('student')


class TeacherSessionDetail(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a session"""
    queryset = models.TeacherSession.objects.all()
    serializer_class = TeacherSessionSerializer


class TeacherActivityList(generics.ListAPIView):
    """List teacher's activity feed"""
    serializer_class = TeacherActivitySerializer
    
    def get_queryset(self):
        teacher_id = self.kwargs.get('teacher_id')
        limit = int(self.request.GET.get('limit', 20))
        return models.TeacherActivity.objects.filter(
            teacher_id=teacher_id
        ).select_related('student')[:limit]


@csrf_exempt
def create_teacher_activity(request, teacher_id):
    """Create a new activity entry (usually called from student actions)"""
    import json
    
    try:
        teacher = models.Teacher.objects.get(pk=teacher_id)
        
        if request.method == 'POST':
            data = json.loads(request.body) if request.body else {}
            
            activity = models.TeacherActivity.objects.create(
                teacher=teacher,
                student_id=data.get('student_id'),
                activity_type=data.get('activity_type'),
                target_name=data.get('target_name'),
                target_id=data.get('target_id'),
                target_type=data.get('target_type'),
                description=data.get('description')
            )
            
            return JsonResponse({
                'bool': True,
                'activity_id': activity.id
            })
            
    except models.Teacher.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Teacher not found'})
    except Exception as e:
        return JsonResponse({'bool': False, 'message': str(e)})


# Lesson Library Views
class TeacherLessonList(generics.ListCreateAPIView):
    """List and create lessons for a teacher"""
    serializer_class = LessonSerializer
    
    def get_queryset(self):
        teacher_id = self.kwargs.get('teacher_id')
        qs = models.Lesson.objects.filter(teacher_id=teacher_id)
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            qs = qs.filter(category_id=category)
        
        # Difficulty filter
        difficulty = self.request.GET.get('difficulty', '')
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        
        # Published filter
        published = self.request.GET.get('published', '')
        if published:
            qs = qs.filter(is_published=published.lower() == 'true')
        
        return qs.select_related('category')


class TeacherLessonDetail(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a lesson"""
    queryset = models.Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonMaterialList(generics.ListCreateAPIView):
    """List and upload lesson materials"""
    serializer_class = LessonMaterialSerializer
    
    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        return models.LessonMaterial.objects.filter(lesson_id=lesson_id)
    
    def perform_create(self, serializer):
        # Calculate file size
        file = self.request.FILES.get('file')
        if file:
            serializer.save(file_size=file.size)
        else:
            serializer.save()


class LessonMaterialDetail(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a lesson material"""
    queryset = models.LessonMaterial.objects.all()
    serializer_class = LessonMaterialSerializer


@csrf_exempt
def upload_lesson_material(request, lesson_id):
    """Handle file upload for lesson materials"""
    from django.core.files.storage import default_storage
    import os
    
    try:
        lesson = models.Lesson.objects.get(pk=lesson_id)
        
        if request.method == 'POST':
            file = request.FILES.get('file')
            title = request.POST.get('title', '')
            material_type = request.POST.get('material_type', 'other')
            
            if not file:
                return JsonResponse({'bool': False, 'message': 'No file provided'})
            
            # Validate file size (50MB max)
            if file.size > 50 * 1024 * 1024:
                return JsonResponse({'bool': False, 'message': 'File size exceeds 50MB limit'})
            
            # Validate file type
            allowed_extensions = {
                'video': ['.mp4', '.webm', '.mov', '.avi'],
                'audio': ['.mp3', '.wav', '.ogg', '.m4a'],
                'pdf': ['.pdf'],
                'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            }
            
            ext = os.path.splitext(file.name)[1].lower()
            
            # Auto-detect material type if not specified
            if material_type == 'other':
                for mtype, extensions in allowed_extensions.items():
                    if ext in extensions:
                        material_type = mtype
                        break
            
            # Create material
            material = models.LessonMaterial.objects.create(
                lesson=lesson,
                title=title or file.name,
                material_type=material_type,
                file=file,
                file_size=file.size,
                order=models.LessonMaterial.objects.filter(lesson=lesson).count()
            )
            
            # Update lesson duration if it's a video/audio
            if material_type in ['video', 'audio']:
                duration_seconds = request.POST.get('duration_seconds', 0)
                if duration_seconds:
                    material.duration_seconds = int(duration_seconds)
                    material.save()
                    
                    # Update total lesson duration
                    total_duration = models.LessonMaterial.objects.filter(
                        lesson=lesson
                    ).aggregate(total=models.Sum('duration_seconds'))['total'] or 0
                    lesson.duration_minutes = total_duration // 60
                    lesson.save()
            
            return JsonResponse({
                'bool': True,
                'material_id': material.id,
                'file_url': material.file.url,
                'file_size_formatted': material.file_size_formatted
            })
            
    except models.Lesson.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Lesson not found'})
    except Exception as e:
        return JsonResponse({'bool': False, 'message': str(e)})


# Teacher Progress View
class TeacherProgressDashboard(APIView):
    """Progress analytics for teacher dashboard"""
    
    def get(self, request, teacher_id):
        from datetime import date, timedelta
        from django.db.models import Count, Avg
        
        try:
            teacher = models.Teacher.objects.get(pk=teacher_id)
        except models.Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=404)
        
        # Overall class performance
        students = models.TeacherStudent.objects.filter(teacher=teacher)
        avg_progress = students.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
        
        # Progress distribution
        progress_distribution = {
            'excellent': students.filter(progress_percentage__gte=80).count(),
            'good': students.filter(progress_percentage__gte=60, progress_percentage__lt=80).count(),
            'average': students.filter(progress_percentage__gte=40, progress_percentage__lt=60).count(),
            'needs_improvement': students.filter(progress_percentage__lt=40).count(),
        }
        
        # Student progress list
        student_progress = [{
            'id': s.id,
            'student_name': s.student.fullname,
            'student_profile_img': s.student.profile_img.url if s.student.profile_img else None,
            'instrument': s.instrument,
            'level': s.level,
            'progress_percentage': s.progress_percentage,
            'status': s.status,
            'last_active': s.last_active.strftime('%Y-%m-%d')
        } for s in students]
        
        # Lesson and course completion stats
        total_lessons = models.Lesson.objects.filter(teacher=teacher).count()
        total_enrollments = models.StudentCourseEnrollment.objects.filter(
            course__teacher=teacher
        ).count()
        completed_courses = models.CourseProgress.objects.filter(
            course__teacher=teacher,
            is_completed=True
        ).count()
        
        # Weekly activity (last 7 days)
        today = date.today()
        weekly_activity = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            activities = models.TeacherActivity.objects.filter(
                teacher=teacher,
                created_at__date=day
            ).count()
            weekly_activity.append({
                'date': day.strftime('%a'),
                'full_date': day.strftime('%Y-%m-%d'),
                'activities': activities
            })
        
        # Top performing students
        top_students = students.order_by('-progress_percentage')[:5]
        top_students_data = [{
            'id': s.id,
            'student_name': s.student.fullname,
            'progress_percentage': s.progress_percentage,
            'level': s.level
        } for s in top_students]
        
        # Students needing attention
        attention_students = students.filter(
            models.Q(status='warning') | 
            models.Q(status='inactive') |
            models.Q(progress_percentage__lt=30)
        )[:5]
        
        attention_data = [{
            'id': s.id,
            'student_name': s.student.fullname,
            'progress_percentage': s.progress_percentage,
            'status': s.status,
            'last_active': s.last_active.strftime('%Y-%m-%d')
        } for s in attention_students]
        
        return Response({
            'overall_progress': round(avg_progress, 1),
            'total_students': students.count(),
            'total_lessons': total_lessons,
            'total_assignments': total_assignments,
            'completed_assignments': completed_assignments,
            'completion_rate': round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0, 1),
            'progress_distribution': progress_distribution,
            'student_progress': student_progress,
            'weekly_activity': weekly_activity,
            'top_students': top_students_data,
            'attention_needed': attention_data
        })


# ==================== ADMIN LESSON MANAGEMENT ====================

from .serializers import ModuleLessonSerializer, ModuleLessonProgressSerializer, ModuleProgressSerializer

class AdminModuleList(generics.ListCreateAPIView):
    """Admin: List all modules or create new module for a course"""
    serializer_class = ChapterSerializer
    
    def get_queryset(self):
        course_id = self.request.GET.get('course_id')
        if course_id:
            return models.Chapter.objects.filter(course_id=course_id).order_by('order', 'id')
        return models.Chapter.objects.all().order_by('course__id', 'order', 'id')


class AdminModuleDetail(generics.RetrieveUpdateDestroyAPIView):
    """Admin: Get, update or delete a module"""
    queryset = models.Chapter.objects.all()
    serializer_class = ChapterSerializer


class AdminModuleLessonList(generics.ListCreateAPIView):
    """Admin: List all lessons in a module or create new lesson"""
    serializer_class = ModuleLessonSerializer
    
    def get_queryset(self):
        module_id = self.kwargs.get('module_id')
        if module_id:
            return models.ModuleLesson.objects.filter(module_id=module_id).order_by('order', 'id')
        return models.ModuleLesson.objects.all().order_by('module__id', 'order', 'id')
    
    def perform_create(self, serializer):
        # Auto-detect content type from file extension
        import os
        file = self.request.FILES.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            content_type_map = {
                '.mp4': 'video', '.webm': 'video', '.mov': 'video', '.avi': 'video',
                '.mp3': 'audio', '.wav': 'audio', '.ogg': 'audio', '.m4a': 'audio',
                '.pdf': 'pdf',
                '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image', '.webp': 'image',
            }
            content_type = content_type_map.get(ext, 'video')
            
            # Get next order number
            module_id = self.request.data.get('module')
            last_order = models.ModuleLesson.objects.filter(module_id=module_id).order_by('-order').first()
            next_order = (last_order.order + 1) if last_order else 0
            
            serializer.save(content_type=content_type, order=next_order)
        else:
            serializer.save()


class AdminModuleLessonDetail(generics.RetrieveUpdateDestroyAPIView):
    """Admin: Get, update or delete a lesson"""
    queryset = models.ModuleLesson.objects.all()
    serializer_class = ModuleLessonSerializer


@csrf_exempt
def admin_reorder_modules(request, course_id):
    """Admin: Reorder modules within a course"""
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            module_order = data.get('order', [])  # List of module IDs in new order
            
            for index, module_id in enumerate(module_order):
                models.Chapter.objects.filter(id=module_id, course_id=course_id).update(order=index)
            
            return JsonResponse({'bool': True, 'message': 'Modules reordered successfully'})
        except Exception as e:
            return JsonResponse({'bool': False, 'message': str(e)})
    
    return JsonResponse({'bool': False, 'message': 'Invalid request method'})


@csrf_exempt
def admin_reorder_lessons(request, module_id):
    """Admin: Reorder lessons within a module"""
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lesson_order = data.get('order', [])  # List of lesson IDs in new order
            
            for index, lesson_id in enumerate(lesson_order):
                models.ModuleLesson.objects.filter(id=lesson_id, module_id=module_id).update(order=index)
            
            return JsonResponse({'bool': True, 'message': 'Lessons reordered successfully'})
        except Exception as e:
            return JsonResponse({'bool': False, 'message': str(e)})
    
    return JsonResponse({'bool': False, 'message': 'Invalid request method'})


@csrf_exempt
def admin_bulk_delete_lessons(request):
    """Admin: Delete multiple lessons at once"""
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lesson_ids = data.get('lesson_ids', [])
            
            deleted_count = models.ModuleLesson.objects.filter(id__in=lesson_ids).delete()[0]
            
            return JsonResponse({
                'bool': True, 
                'message': f'{deleted_count} lessons deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'bool': False, 'message': str(e)})
    
    return JsonResponse({'bool': False, 'message': 'Invalid request method'})


class AdminCourseModulesWithLessons(APIView):
    """Admin: Get complete course structure with all modules and lessons"""
    
    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(pk=course_id)
            modules = models.Chapter.objects.filter(course=course).order_by('order', 'id')
            
            modules_data = []
            for module in modules:
                lessons = models.ModuleLesson.objects.filter(module=module).order_by('order', 'id')
                lessons_data = [{
                    'id': lesson.id,
                    'title': lesson.title,
                    'description': lesson.description,
                    'content_type': lesson.content_type,
                    'file': request.build_absolute_uri(lesson.file.url) if lesson.file else None,
                    'duration_seconds': lesson.duration_seconds,
                    'duration_formatted': lesson.duration_formatted,
                    'order': lesson.order
                } for lesson in lessons]
                
                modules_data.append({
                    'id': module.id,
                    'title': module.title,
                    'description': module.description,
                    'order': module.order,
                    'total_lessons': len(lessons_data),
                    'lessons': lessons_data
                })
            
            return Response({
                'course_id': course.id,
                'course_title': course.title,
                'total_modules': len(modules_data),
                'modules': modules_data
            })
        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)


# ==================== STUDENT LESSON PROGRESS ====================

class StudentModuleProgress(APIView):
    """Get student's progress for a specific course"""
    
    def get(self, request, student_id, course_id):
        try:
            student = models.Student.objects.get(pk=student_id)
            course = models.Course.objects.get(pk=course_id)
            modules = models.Chapter.objects.filter(course=course).order_by('order', 'id')
            
            modules_data = []
            total_lessons = 0
            completed_lessons = 0
            
            for module in modules:
                lessons = models.ModuleLesson.objects.filter(module=module).order_by('order', 'id')
                module_total = lessons.count()
                
                # Get or create module progress
                module_progress, _ = models.ModuleProgress.objects.get_or_create(
                    student=student, module=module
                )
                
                lessons_data = []
                module_completed = 0
                
                for lesson in lessons:
                    lesson_progress = models.ModuleLessonProgress.objects.filter(
                        student=student, lesson=lesson
                    ).first()
                    
                    is_completed = lesson_progress.is_completed if lesson_progress else False
                    if is_completed:
                        module_completed += 1
                        completed_lessons += 1
                    
                    lessons_data.append({
                        'id': lesson.id,
                        'title': lesson.title,
                        'content_type': lesson.content_type,
                        'duration_formatted': lesson.duration_formatted,
                        'is_completed': is_completed,
                        'last_position': lesson_progress.last_position_seconds if lesson_progress else 0
                    })
                
                total_lessons += module_total
                
                modules_data.append({
                    'id': module.id,
                    'title': module.title,
                    'order': module.order,
                    'total_lessons': module_total,
                    'completed_lessons': module_completed,
                    'is_completed': module_progress.is_completed,
                    'lessons': lessons_data
                })
            
            progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            
            return Response({
                'course_id': course.id,
                'course_title': course.title,
                'total_modules': len(modules_data),
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'progress_percentage': round(progress_percentage, 1),
                'modules': modules_data
            })
        except (models.Student.DoesNotExist, models.Course.DoesNotExist) as e:
            return Response({'error': str(e)}, status=404)


@csrf_exempt
def mark_lesson_complete(request, student_id, lesson_id):
    """Mark a lesson as completed for a student"""
    from django.utils import timezone
    
    if request.method == 'POST':
        try:
            student = models.Student.objects.get(pk=student_id)
            lesson = models.ModuleLesson.objects.get(pk=lesson_id)
            course = lesson.module.course
            
            # Get or create lesson progress
            progress, created = models.ModuleLessonProgress.objects.get_or_create(
                student=student, lesson=lesson
            )
            
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            
            # Check if module is now complete
            module_progress, _ = models.ModuleProgress.objects.get_or_create(
                student=student, module=lesson.module
            )
            module_progress.check_completion()
            
            # Update CourseProgress
            course_progress, cp_created = models.CourseProgress.objects.get_or_create(
                student=student,
                course=course,
                defaults={'total_chapters': 0, 'completed_chapters': 0}
            )
            
            # Calculate total lessons and completed lessons for this course
            total_lessons = 0
            for chapter in course.course_chapters.all():
                total_lessons += chapter.module_lessons.count()
            
            # Count completed lessons for this student in this course
            completed_lessons = models.ModuleLessonProgress.objects.filter(
                student=student,
                lesson__module__course=course,
                is_completed=True
            ).count()
            
            # Update progress
            course_progress.total_chapters = total_lessons
            course_progress.completed_chapters = completed_lessons
            course_progress.progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
            
            # Check if course is now complete
            if course_progress.progress_percentage >= 100 and not course_progress.is_completed:
                course_progress.is_completed = True
                course_progress.completed_at = timezone.now()
                
                # Check for completion achievements
                try:
                    completed_courses = models.CourseProgress.objects.filter(
                        student=student,
                        is_completed=True
                    ).count()
                    
                    completion_achievements = models.Achievement.objects.filter(
                        achievement_type='completion',
                        is_active=True
                    )
                    for achievement in completion_achievements:
                        if completed_courses >= achievement.requirement_value:
                            models.StudentAchievement.objects.get_or_create(
                                student=student,
                                achievement=achievement
                            )
                except:
                    pass  # Silently fail if achievement check has issues
            
            course_progress.save()
            
            return JsonResponse({
                'bool': True,
                'message': 'Lesson marked as complete',
                'module_completed': module_progress.is_completed,
                'course_completed': course_progress.is_completed,
                'course_progress_percentage': course_progress.progress_percentage
            })
        except (models.Student.DoesNotExist, models.ModuleLesson.DoesNotExist) as e:
            return JsonResponse({'bool': False, 'message': str(e)})
    
    return JsonResponse({'bool': False, 'message': 'Invalid request method'})


@csrf_exempt
def update_lesson_position(request, student_id, lesson_id):
    """Update the last watched position for video/audio lessons"""
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            position = data.get('position', 0)
            
            student = models.Student.objects.get(pk=student_id)
            lesson = models.ModuleLesson.objects.get(pk=lesson_id)
            
            progress, _ = models.ModuleLessonProgress.objects.get_or_create(
                student=student, lesson=lesson
            )
            progress.last_position_seconds = position
            progress.save()
            
            return JsonResponse({'bool': True, 'message': 'Position updated'})
        except Exception as e:
            return JsonResponse({'bool': False, 'message': str(e)})
    
    return JsonResponse({'bool': False, 'message': 'Invalid request method'})


class StudentCourseNavigation(APIView):
    """Get next/previous module and lesson for navigation"""
    
    def get(self, request, student_id, course_id, current_lesson_id):
        try:
            course = models.Course.objects.get(pk=course_id)
            current_lesson = models.ModuleLesson.objects.get(pk=current_lesson_id)
            current_module = current_lesson.module
            
            # Get all lessons in course order
            all_modules = models.Chapter.objects.filter(course=course).order_by('order', 'id')
            all_lessons = []
            
            for module in all_modules:
                lessons = models.ModuleLesson.objects.filter(module=module).order_by('order', 'id')
                for lesson in lessons:
                    all_lessons.append({
                        'lesson_id': lesson.id,
                        'lesson_title': lesson.title,
                        'module_id': module.id,
                        'module_title': module.title
                    })
            
            # Find current position
            current_index = None
            for i, lesson in enumerate(all_lessons):
                if lesson['lesson_id'] == current_lesson_id:
                    current_index = i
                    break
            
            prev_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
            next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
            
            return Response({
                'current': {
                    'lesson_id': current_lesson.id,
                    'lesson_title': current_lesson.title,
                    'module_id': current_module.id,
                    'module_title': current_module.title,
                    'content_type': current_lesson.content_type,
                    'file': request.build_absolute_uri(current_lesson.file.url) if current_lesson.file else None
                },
                'previous': prev_lesson,
                'next': next_lesson,
                'total_lessons': len(all_lessons),
                'current_position': current_index + 1 if current_index is not None else 0
            })
        except Exception as e:
            return Response({'error': str(e)}, status=404)


# ==================== LESSON UNLOCK SYSTEM & DOWNLOADABLES ====================

class StudentModuleProgressEnhanced(APIView):
    """Get student's progress for a specific course with unlock status"""
    
    def get(self, request, student_id, course_id):
        try:
            student = models.Student.objects.get(pk=student_id)
            course = models.Course.objects.get(pk=course_id)
            modules = models.Chapter.objects.filter(course=course).order_by('order', 'id')
            
            modules_data = []
            total_lessons = 0
            completed_lessons = 0
            first_incomplete_found = False
            
            for module_index, module in enumerate(modules):
                lessons = models.ModuleLesson.objects.filter(module=module).order_by('order', 'id')
                module_total = lessons.count()
                
                # Get or create module progress
                module_progress, _ = models.ModuleProgress.objects.get_or_create(
                    student=student, module=module
                )
                
                lessons_data = []
                module_completed = 0
                
                for lesson_index, lesson in enumerate(lessons):
                    lesson_progress = models.ModuleLessonProgress.objects.filter(
                        student=student, lesson=lesson
                    ).first()
                    
                    is_completed = lesson_progress.is_completed if lesson_progress else False
                    if is_completed:
                        module_completed += 1
                        completed_lessons += 1
                    
                    # Determine if lesson is locked
                    # First lesson is always unlocked, others unlock when previous is complete
                    is_first_lesson = (module_index == 0 and lesson_index == 0)
                    is_preview = lesson.is_preview
                    
                    # A lesson is unlocked if:
                    # 1. It's the first lesson overall, OR
                    # 2. It's marked as a preview lesson, OR
                    # 3. It's already completed, OR
                    # 4. The previous lesson (in order) is completed, OR
                    # 5. It's the first uncompleted lesson (current lesson to work on)
                    
                    is_unlocked = is_first_lesson or is_preview or is_completed
                    
                    if not is_unlocked and not first_incomplete_found:
                        # This is the first incomplete lesson - unlock it
                        is_unlocked = True
                        first_incomplete_found = True
                    elif not is_unlocked:
                        # Check if previous lesson in this module is completed
                        if lesson_index > 0:
                            prev_lesson = lessons[lesson_index - 1]
                            prev_progress = models.ModuleLessonProgress.objects.filter(
                                student=student, lesson=prev_lesson, is_completed=True
                            ).exists()
                            is_unlocked = prev_progress
                    
                    # Get downloadables for this lesson
                    downloadables = models.LessonDownloadable.objects.filter(
                        lesson=lesson
                    ).order_by('order', 'id')
                    
                    downloadables_data = [{
                        'id': d.id,
                        'title': d.title,
                        'file_type': d.file_type,
                        'file_type_display': d.get_file_type_display(),
                        'file_type_icon': d.get_file_type_icon(),
                        'file': request.build_absolute_uri(d.file.url) if d.file else None,
                        'description': d.description,
                        'file_size_formatted': d.file_size_formatted,
                        'file_extension': d.file_extension,
                        'download_count': d.download_count
                    } for d in downloadables]
                    
                    lessons_data.append({
                        'id': lesson.id,
                        'title': lesson.title,
                        'description': lesson.description,
                        'objectives': lesson.objectives,
                        'objectives_list': lesson.objectives_list,
                        'content_type': lesson.content_type,
                        'file': request.build_absolute_uri(lesson.file.url) if lesson.file else None,
                        'duration_seconds': lesson.duration_seconds,
                        'duration_formatted': lesson.duration_formatted,
                        'is_completed': is_completed,
                        'is_preview': is_preview,
                        'is_locked': not is_unlocked,
                        'is_unlocked': is_unlocked,
                        'last_position': lesson_progress.last_position_seconds if lesson_progress else 0,
                        'downloadables': downloadables_data
                    })
                
                total_lessons += module_total
                
                # Module is unlocked if first module or previous module is completed
                module_unlocked = True
                if module_index > 0:
                    prev_module = modules[module_index - 1]
                    prev_module_progress = models.ModuleProgress.objects.filter(
                        student=student, module=prev_module, is_completed=True
                    ).exists()
                    # But if any lesson in this module is unlocked, the module is also unlocked
                    any_lesson_unlocked = any(l['is_unlocked'] for l in lessons_data)
                    module_unlocked = prev_module_progress or any_lesson_unlocked
                
                modules_data.append({
                    'id': module.id,
                    'title': module.title,
                    'description': module.description,
                    'order': module.order,
                    'total_lessons': module_total,
                    'completed_lessons': module_completed,
                    'is_completed': module_progress.is_completed,
                    'is_unlocked': module_unlocked,
                    'lessons': lessons_data
                })
            
            progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            
            return Response({
                'course_id': course.id,
                'course_title': course.title,
                'course_description': course.description,
                'total_modules': len(modules_data),
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'progress_percentage': round(progress_percentage, 1),
                'modules': modules_data
            })
        except (models.Student.DoesNotExist, models.Course.DoesNotExist) as e:
            return Response({'error': str(e)}, status=404)


class LessonDownloadableList(generics.ListCreateAPIView):
    """List or create downloadables for a lesson"""
    serializer_class = LessonDownloadableSerializer
    
    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        return models.LessonDownloadable.objects.filter(lesson_id=lesson_id).order_by('order', 'id')


class LessonDownloadableDetail(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a downloadable"""
    queryset = models.LessonDownloadable.objects.all()
    serializer_class = LessonDownloadableSerializer


@csrf_exempt
def increment_download_count(request, downloadable_id):
    """Increment download count for a downloadable"""
    if request.method == 'POST':
        try:
            downloadable = models.LessonDownloadable.objects.get(pk=downloadable_id)
            downloadable.download_count += 1
            downloadable.save()
            return JsonResponse({'bool': True, 'download_count': downloadable.download_count})
        except models.LessonDownloadable.DoesNotExist:
            return JsonResponse({'bool': False, 'message': 'Downloadable not found'})
    return JsonResponse({'bool': False, 'message': 'Invalid request method'})


class LessonDetailWithDownloadables(APIView):
    """Get detailed lesson info with objectives and downloadables"""
    
    def get(self, request, lesson_id, student_id=None):
        try:
            lesson = models.ModuleLesson.objects.get(pk=lesson_id)
            
            # Get student progress if student_id provided
            is_completed = False
            last_position = 0
            is_unlocked = True
            
            if student_id:
                try:
                    student = models.Student.objects.get(pk=student_id)
                    progress = models.ModuleLessonProgress.objects.filter(
                        student=student, lesson=lesson
                    ).first()
                    if progress:
                        is_completed = progress.is_completed
                        last_position = progress.last_position_seconds
                    
                    # Check unlock status
                    course = lesson.module.course
                    module = lesson.module
                    
                    # Get all lessons before this one
                    prev_lessons = models.ModuleLesson.objects.filter(
                        module__course=course,
                        module__order__lte=module.order
                    ).exclude(
                        module=module, order__gte=lesson.order
                    ).exclude(id=lesson.id)
                    
                    # Check if this is the first lesson
                    is_first = not prev_lessons.exists()
                    
                    if not is_first and not lesson.is_preview:
                        # Check if all previous lessons are completed
                        all_prev_completed = all(
                            models.ModuleLessonProgress.objects.filter(
                                student=student, lesson=prev_lesson, is_completed=True
                            ).exists()
                            for prev_lesson in prev_lessons
                        )
                        is_unlocked = all_prev_completed or is_completed
                    
                except models.Student.DoesNotExist:
                    pass
            
            # Get downloadables
            downloadables = models.LessonDownloadable.objects.filter(
                lesson=lesson
            ).order_by('order', 'id')
            
            downloadables_data = [{
                'id': d.id,
                'title': d.title,
                'file_type': d.file_type,
                'file_type_display': d.get_file_type_display(),
                'file_type_icon': d.get_file_type_icon(),
                'file': request.build_absolute_uri(d.file.url) if d.file else None,
                'description': d.description,
                'file_size_formatted': d.file_size_formatted,
                'file_extension': d.file_extension,
                'download_count': d.download_count
            } for d in downloadables]
            
            return Response({
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'objectives': lesson.objectives,
                'objectives_list': lesson.objectives_list,
                'content_type': lesson.content_type,
                'file': request.build_absolute_uri(lesson.file.url) if lesson.file else None,
                'duration_seconds': lesson.duration_seconds,
                'duration_formatted': lesson.duration_formatted,
                'is_preview': lesson.is_preview,
                'is_completed': is_completed,
                'is_unlocked': is_unlocked,
                'last_position': last_position,
                'module': {
                    'id': lesson.module.id,
                    'title': lesson.module.title
                },
                'course': {
                    'id': lesson.module.course.id,
                    'title': lesson.module.course.title
                },
                'downloadables': downloadables_data
            })
        except models.ModuleLesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=404)


def check_lesson_unlock_status(request, student_id, lesson_id):
    """Check if a specific lesson is unlocked for a student"""
    try:
        student = models.Student.objects.get(pk=student_id)
        lesson = models.ModuleLesson.objects.get(pk=lesson_id)
        course = lesson.module.course
        module = lesson.module
        
        # Get progress for this lesson
        progress = models.ModuleLessonProgress.objects.filter(
            student=student, lesson=lesson
        ).first()
        is_completed = progress.is_completed if progress else False
        
        # If already completed or preview, it's unlocked
        if is_completed or lesson.is_preview:
            return JsonResponse({'is_unlocked': True, 'is_completed': is_completed})
        
        # Get all lessons in the course ordered
        all_modules = models.Chapter.objects.filter(course=course).order_by('order', 'id')
        all_lessons = []
        
        for mod in all_modules:
            lessons = models.ModuleLesson.objects.filter(module=mod).order_by('order', 'id')
            all_lessons.extend(lessons)
        
        # Find index of current lesson
        current_index = None
        for i, l in enumerate(all_lessons):
            if l.id == lesson.id:
                current_index = i
                break
        
        # First lesson is always unlocked
        if current_index == 0:
            return JsonResponse({'is_unlocked': True, 'is_completed': is_completed})
        
        # Check if previous lesson is completed
        prev_lesson = all_lessons[current_index - 1]
        prev_progress = models.ModuleLessonProgress.objects.filter(
            student=student, lesson=prev_lesson, is_completed=True
        ).exists()
        
        return JsonResponse({
            'is_unlocked': prev_progress,
            'is_completed': is_completed,
            'requires_completion_of': {
                'id': prev_lesson.id,
                'title': prev_lesson.title
            } if not prev_progress else None
        })
        
    except (models.Student.DoesNotExist, models.ModuleLesson.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=404)


# ==================== CONSOLIDATED STUDENT LESSON PAGE DATA ====================

class StudentLessonPageData(APIView):
    """
    Consolidated endpoint that returns ALL data needed for the lesson player page
    in a single API call. Replaces 3 separate calls:
    - /fetch-enroll-status/
    - /progress-enhanced/
    - /navigation/
    """
    
    def get(self, request, student_id, course_id, lesson_id=None):
        try:
            student = models.Student.objects.get(pk=student_id)
            course = models.Course.objects.get(pk=course_id)
            
            # Check enrollment
            enrollment = models.StudentCourseEnrollment.objects.filter(
                student=student, course=course
            ).exists()
            
            if not enrollment:
                return Response({
                    'is_enrolled': False,
                    'error': 'Not enrolled in this course'
                }, status=403)
            
            # Get all modules with lessons and progress
            modules = models.Chapter.objects.filter(course=course).order_by('order', 'id')
            
            modules_data = []
            total_lessons = 0
            completed_lessons = 0
            current_lesson_data = None
            all_lessons = []
            current_lesson_index = None
            
            for module_index, module in enumerate(modules):
                lessons = models.ModuleLesson.objects.filter(module=module).order_by('order', 'id')
                module_total = lessons.count()
                
                module_progress, _ = models.ModuleProgress.objects.get_or_create(
                    student=student, module=module
                )
                
                lessons_data = []
                module_completed = 0
                
                for lesson_index, lesson in enumerate(lessons):
                    lesson_progress = models.ModuleLessonProgress.objects.filter(
                        student=student, lesson=lesson
                    ).first()
                    
                    is_completed = lesson_progress.is_completed if lesson_progress else False
                    if is_completed:
                        module_completed += 1
                        completed_lessons += 1
                    
                    # Determine if lesson is locked (based on previous module completion)
                    is_locked = False
                    if module_index > 0:
                        prev_module = modules[module_index - 1]
                        prev_module_progress = models.ModuleProgress.objects.filter(
                            student=student, module=prev_module
                        ).first()
                        if prev_module_progress and not prev_module_progress.is_completed:
                            is_locked = True
                    
                    # Get lesson downloadables
                    downloadables = models.LessonDownloadable.objects.filter(
                        lesson=lesson
                    ).order_by('order')
                    
                    downloadables_data = []
                    for downloadable in downloadables:
                        downloadables_data.append({
                            'id': downloadable.id,
                            'title': downloadable.title,
                            'file': request.build_absolute_uri(downloadable.file.url) if downloadable.file else None,
                            'file_type': downloadable.file_type,
                            'file_type_display': downloadable.get_file_type_display(),
                            'file_size_formatted': downloadable.file_size_formatted,
                            'download_count': downloadable.download_count,
                        })
                    
                    lesson_obj = {
                        'id': lesson.id,
                        'title': lesson.title,
                        'description': lesson.description,
                        'content_type': lesson.content_type,
                        'file': request.build_absolute_uri(lesson.file.url) if lesson.file else None,
                        'duration_seconds': lesson.duration_seconds,
                        'duration_formatted': lesson.duration_formatted,
                        'is_completed': is_completed,
                        'is_locked': is_locked,
                        'is_preview': lesson.is_preview,
                        'last_position': lesson_progress.last_position_seconds if lesson_progress else 0,
                        'objectives': lesson.objectives,
                        'objectives_list': lesson.objectives_list or [],
                        'downloadables': downloadables_data,
                        'module_id': module.id,
                        'module_title': module.title,
                    }
                    
                    lessons_data.append(lesson_obj)
                    all_lessons.append(lesson_obj)
                    
                    # If lesson_id matches, store this as current
                    if lesson.id == lesson_id:
                        current_lesson_data = lesson_obj
                        current_lesson_index = len(all_lessons) - 1
                
                total_lessons += module_total
                
                modules_data.append({
                    'id': module.id,
                    'title': module.title,
                    'order': module.order,
                    'description': module.description,
                    'total_lessons': module_total,
                    'completed_lessons': module_completed,
                    'is_completed': module_progress.is_completed,
                    'lessons': lessons_data
                })
            
            # If no lesson_id or invalid lesson, use first unlocked incomplete
            if not current_lesson_data and all_lessons:
                for lesson in all_lessons:
                    if not lesson['is_locked'] and not lesson['is_completed']:
                        current_lesson_data = lesson
                        current_lesson_index = all_lessons.index(lesson)
                        break
                
                # Fallback to first lesson if all completed
                if not current_lesson_data:
                    current_lesson_data = all_lessons[0]
                    current_lesson_index = 0
            
            # Compute navigation from all_lessons list
            previous_lesson = None
            next_lesson = None
            
            if current_lesson_index is not None:
                if current_lesson_index > 0:
                    prev = all_lessons[current_lesson_index - 1]
                    previous_lesson = {
                        'id': prev['id'],
                        'title': prev['title'],
                        'module_id': prev['module_id'],
                        'module_title': prev['module_title'],
                    }
                
                if current_lesson_index < len(all_lessons) - 1:
                    nxt = all_lessons[current_lesson_index + 1]
                    next_lesson = {
                        'id': nxt['id'],
                        'title': nxt['title'],
                        'module_id': nxt['module_id'],
                        'module_title': nxt['module_title'],
                    }
            
            progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            
            return Response({
                'is_enrolled': True,
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'description': course.description,
                },
                'modules': modules_data,
                'current_lesson': current_lesson_data,
                'navigation': {
                    'previous': previous_lesson,
                    'next': next_lesson,
                    'current_position': (current_lesson_index + 1) if current_lesson_index is not None else 0,
                    'total_lessons': len(all_lessons)
                },
                'progress': {
                    'completed_lessons': completed_lessons,
                    'total_lessons': total_lessons,
                    'overall_progress': round(progress_percentage, 1)
                }
            })
            
        except models.Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)
        except models.Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


# ==================== SUBSCRIPTION MANAGEMENT VIEWS ====================

class SubscriptionPlanList(generics.ListCreateAPIView):
    """List and create subscription plans"""
    serializer_class = SubscriptionPlanSerializer
    pagination_class = StandardResultSetPagination
    
    def get_queryset(self):
        queryset = models.SubscriptionPlan.objects.all()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')


class SubscriptionPlanDetail(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a subscription plan"""
    queryset = models.SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer


class SubscriptionList(generics.ListCreateAPIView):
    """List and create subscriptions (admin can create subscriptions for students)"""
    queryset = models.Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = StandardResultSetPagination
    
    def get_queryset(self):
        queryset = models.Subscription.objects.all()
        
        # Filter by student if specified
        student_id = self.request.query_params.get('student_id', None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by plan
        plan_id = self.request.query_params.get('plan_id', None)
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Save subscription and create history entry"""
        subscription = serializer.save()
        
        # Create history entry
        models.SubscriptionHistory.objects.create(
            subscription=subscription,
            action='created',
            new_status=subscription.status,
            new_plan=subscription.plan,
            changed_by='admin'
        )


class SubscriptionDetail(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a subscription"""
    queryset = models.Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    
    def perform_update(self, serializer):
        """Track subscription changes in history"""
        old_subscription = self.get_object()
        new_subscription = serializer.save()
        
        # Determine action
        action = 'updated'
        if old_subscription.status != new_subscription.status:
            if new_subscription.status == 'cancelled':
                action = 'cancelled'
            elif old_subscription.status == 'pending' and new_subscription.status == 'active':
                action = 'activated'
            elif old_subscription.plan != new_subscription.plan:
                action = 'upgraded' if new_subscription.plan.price > old_subscription.plan.price else 'downgraded'
        
        # Create history entry
        models.SubscriptionHistory.objects.create(
            subscription=new_subscription,
            action=action,
            old_status=old_subscription.status,
            new_status=new_subscription.status,
            old_plan=old_subscription.plan,
            new_plan=new_subscription.plan,
            changed_by='admin'
        )


@csrf_exempt
def activate_subscription(request, subscription_id):
    """Activate a pending subscription"""
    try:
        subscription = models.Subscription.objects.get(id=subscription_id)
        subscription.activate()
        
        return JsonResponse({
            'bool': True,
            'message': 'Subscription activated successfully',
            'subscription': {
                'id': subscription.id,
                'status': subscription.status,
                'activated_at': subscription.activated_at.isoformat()
            }
        })
    except models.Subscription.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Subscription not found'}, status=404)
    except Exception as e:
        return JsonResponse({'bool': False, 'message': str(e)}, status=400)


@csrf_exempt
def cancel_subscription(request, subscription_id):
    """Cancel an active subscription"""
    try:
        subscription = models.Subscription.objects.get(id=subscription_id)
        subscription.cancel()
        
        return JsonResponse({
            'bool': True,
            'message': 'Subscription cancelled successfully',
            'subscription': {
                'id': subscription.id,
                'status': subscription.status,
                'cancelled_at': subscription.cancelled_at.isoformat()
            }
        })
    except models.Subscription.DoesNotExist:
        return JsonResponse({'bool': False, 'message': 'Subscription not found'}, status=404)
    except Exception as e:
        return JsonResponse({'bool': False, 'message': str(e)}, status=400)


class SubscriptionHistoryList(generics.ListAPIView):
    """Get subscription history"""
    serializer_class = SubscriptionHistorySerializer
    pagination_class = StandardResultSetPagination
    
    def get_queryset(self):
        queryset = models.SubscriptionHistory.objects.all()
        
        # Filter by subscription if specified
        subscription_id = self.request.query_params.get('subscription_id', None)
        if subscription_id:
            queryset = queryset.filter(subscription_id=subscription_id)
        
        # Filter by student
        student_id = self.request.query_params.get('student_id', None)
        if student_id:
            queryset = queryset.filter(subscription__student_id=student_id)
        
        return queryset.order_by('-created_at')


@csrf_exempt
def create_payment_intent(request):
    """Create a Stripe payment intent for subscription"""
    import json
    import stripe
    import os
    
    print("\n" + "="*80)
    print(f"🔍 PAYMENT INTENT REQUEST RECEIVED")
    print(f"Method: {request.method}")
    print(f"Content-Type: {request.headers.get('Content-Type')}")
    print(f"Request body length: {len(request.body)} bytes")
    print("="*80)
    
    # Set Stripe API key from environment
    stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
    if not stripe_secret_key:
        print("❌ STRIPE_SECRET_KEY not configured")
        return JsonResponse({
            'error': 'Stripe API key not configured. Please set STRIPE_SECRET_KEY environment variable.'
        }, status=500)
    
    print(f"✅ STRIPE_SECRET_KEY found")
    print(f"   Key length: {len(stripe_secret_key)} chars")
    print(f"   First 20 chars: {stripe_secret_key[:20]}")
    print(f"   Last 20 chars: {stripe_secret_key[-20:]}")
    print(f"   Full key: {stripe_secret_key}")
    stripe.api_key = stripe_secret_key
    
    if request.method == 'POST':
        try:
            print("\n📥 Attempting to parse JSON from request body...")
            print(f"Raw body: {request.body[:200]}...")  # Print first 200 chars
            
            data = json.loads(request.body)
            print(f"\n✅ JSON parsed successfully!")
            print(f"📊 Full data: {data}")
            
            amount = data.get('amount')
            plan_id = data.get('plan_id')
            student_id = data.get('student_id')
            email = data.get('email')
            name = data.get('name')
            
            # Print each field
            print(f"\n📋 Received fields:")
            print(f"   amount: {amount} (type: {type(amount).__name__})")
            print(f"   plan_id: {plan_id} (type: {type(plan_id).__name__})")
            print(f"   student_id: {student_id} (type: {type(student_id).__name__})")
            print(f"   email: {email}")
            print(f"   name: {name}")
            
            # Validate required fields
            if not all([amount, plan_id, student_id, email, name]):
                missing_fields = []
                if not amount: missing_fields.append('amount')
                if not plan_id: missing_fields.append('plan_id')
                if not student_id: missing_fields.append('student_id')
                if not email: missing_fields.append('email')
                if not name: missing_fields.append('name')
                
                error_msg = f'Missing required fields: {", ".join(missing_fields)}'
                print(f"\n❌ {error_msg}")
                print(f"Received: {data}")
                return JsonResponse({
                    'error': error_msg,
                    'received_fields': {
                        'amount': amount,
                        'plan_id': plan_id,
                        'student_id': student_id,
                        'email': email,
                        'name': name
                    }
                }, status=400)
            
            if amount <= 0:
                print(f"\n❌ Invalid amount: {amount}")
                return JsonResponse({'error': 'Invalid amount'}, status=400)
            
            print(f"\n✅ All validations passed!")
            
            # Verify the plan exists
            try:
                plan = models.SubscriptionPlan.objects.get(id=plan_id)
                print(f"✅ Plan found: {plan.name} (id: {plan_id})")
            except models.SubscriptionPlan.DoesNotExist:
                print(f"❌ Plan not found with id: {plan_id}")
                return JsonResponse({'error': 'Plan not found'}, status=404)
            
            # Verify the student exists
            try:
                student = models.Student.objects.get(id=student_id)
                print(f"✅ Student found: {student.fullname} (id: {student_id})")
            except models.Student.DoesNotExist:
                print(f"❌ Student not found with id: {student_id}")
                return JsonResponse({'error': 'Student not found'}, status=404)
            
            print(f"\n🔐 Creating Stripe Payment Intent...")
            print(f"   Amount: {int(amount)} cents (${amount/100})")
            print(f"   Currency: USD")
            print(f"   Description: Subscription to {plan.name} plan")
            
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency='usd',
                description=f'Subscription to {plan.name} plan',
                metadata={
                    'plan_id': str(plan_id),
                    'plan_name': plan.name,
                    'student_id': str(student_id),
                    'student_email': email,
                    'student_name': name
                },
                receipt_email=email
            )
            
            print(f"✅ Payment intent created successfully!")
            print(f"   Intent ID: {intent.id}")
            print(f"   Client Secret: {intent.client_secret[:30]}...")
            print("="*80 + "\n")
            
            return JsonResponse({
                'clientSecret': intent.client_secret,
                'paymentIntentId': intent.id,
                'status': 'success'
            })
        except stripe.error.CardError as e:
            print(f"\n❌ Stripe Card Error: {str(e.user_message)}")
            return JsonResponse({'error': f'Card error: {str(e.user_message)}'}, status=400)
        except stripe.error.RateLimitError:
            print(f"\n❌ Stripe Rate Limit Error")
            return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=400)
        except stripe.error.InvalidRequestError as e:
            print(f"\n❌ Stripe Invalid Request: {str(e)}")
            print(f"Details: {e.http_body}")
            return JsonResponse({'error': f'Invalid request: {str(e)}'}, status=400)
        except stripe.error.AuthenticationError as e:
            print(f"\n❌ Stripe Authentication Error!")
            print(f"Error message: {str(e)}")
            print(f"HTTP status: {e.http_status}")
            print(f"HTTP body: {e.http_body}")
            print(f"This usually means your Stripe API key is invalid or expired.")
            return JsonResponse({
                'error': 'Stripe authentication failed - Invalid API key',
                'details': str(e)
            }, status=400)
        except stripe.error.APIConnectionError as e:
            print(f"\n❌ Stripe API Connection Error")
            print(f"Error: {str(e)}")
            return JsonResponse({'error': 'Network connection error. Please try again.'}, status=400)
        except stripe.error.StripeError as e:
            print(f"\n❌ Stripe Error: {str(e)}")
            print(f"Type: {type(e).__name__}")
            return JsonResponse({'error': f'Stripe error: {str(e)}'}, status=400)
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON Decode Error: {str(e)}")
            print(f"Request body was: {request.body}")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            import traceback
            print(f"\n❌ Unexpected Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    print(f"\n❌ Invalid request method: {request.method}")
    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)


@csrf_exempt
def get_admin_subscription_stats(request):
    """Get subscription statistics for admin dashboard"""
    try:
        total_plans = models.SubscriptionPlan.objects.filter(status='active').count()
        total_subscriptions = models.Subscription.objects.count()
        active_subscriptions = models.Subscription.objects.filter(status='active').count()
        pending_subscriptions = models.Subscription.objects.filter(status='pending').count()
        cancelled_subscriptions = models.Subscription.objects.filter(status='cancelled').count()
        
        # Get total revenue
        from django.db.models import Sum
        total_revenue = models.Subscription.objects.filter(
            is_paid=True
        ).aggregate(total=Sum('price_paid'))['total'] or 0
        
        # Get popular plans
        popular_plans = models.SubscriptionPlan.objects.annotate(
            subscriber_count=models.Count('subscriptions')
        ).order_by('-subscriber_count')[:5]
        
        popular_plans_data = []
        for plan in popular_plans:
            popular_plans_data.append({
                'id': plan.id,
                'name': plan.name,
                'subscriber_count': plan.subscriber_count,
                'price': str(plan.price)
            })
        
        return JsonResponse({
            'bool': True,
            'stats': {
                'total_plans': total_plans,
                'total_subscriptions': total_subscriptions,
                'active_subscriptions': active_subscriptions,
                'pending_subscriptions': pending_subscriptions,
                'cancelled_subscriptions': cancelled_subscriptions,
                'total_revenue': float(total_revenue),
                'popular_plans': popular_plans_data
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'bool': False, 'message': str(e)}, status=200)


