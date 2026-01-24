from rest_framework import serializers
from . import models
from django.contrib.flatpages.models import FlatPage


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Teacher
        fields=['id','full_name','email','password','qualification','mobile_no','skills','profile_img','teacher_courses','skill_list','total_teacher_course','face_url','insta_url','twit_url','web_url','you_url']
    def __init__(self, *args, **kwargs):
            super(TeacherSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=models.CourseCategory
        fields=['id','title','description','total_courses']
    def __init__(self, *args, **kwargs):
            super(CategorySerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2

class CourseSerializer(serializers.ModelSerializer):
    course_chapters = serializers.SerializerMethodField()
    total_enrolled_students = serializers.SerializerMethodField()
    course_rating = serializers.SerializerMethodField()
    course_views = serializers.IntegerField(read_only=True)
    
    class Meta:
        model=models.Course
        fields=['id','category','teacher','title','description','featured_img','techs','course_chapters','related_videos','teach_list','total_enrolled_students','course_rating','course_views']
    
    def get_course_chapters(self, obj):
        chapters = obj.course_chapters.all().order_by('order', 'id')
        return ChapterSerializer(chapters, many=True, context=self.context).data
    
    def get_total_enrolled_students(self, obj):
        return obj.total_enrolled_students()
    
    def get_course_rating(self, obj):
        return obj.course_rating()
    
    def __init__(self, *args, **kwargs):
            super(CourseSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2

class LessonDownloadableSerializer(serializers.ModelSerializer):
    """Serializer for lesson downloadable resources"""
    file_size_formatted = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    file_type_icon = serializers.CharField(source='get_file_type_icon', read_only=True)
    
    class Meta:
        model = models.LessonDownloadable
        fields = ['id', 'lesson', 'title', 'file_type', 'file_type_display', 
                  'file_type_icon', 'file', 'description', 'order', 
                  'download_count', 'file_size_formatted', 'file_extension', 'created_at']
    
    def __init__(self, *args, **kwargs):
        super(LessonDownloadableSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class ModuleLessonSerializer(serializers.ModelSerializer):
    """Serializer for individual lessons within a module"""
    duration_formatted = serializers.ReadOnlyField()
    file_size_formatted = serializers.ReadOnlyField()
    objectives_list = serializers.ReadOnlyField()
    downloadables = LessonDownloadableSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.ModuleLesson
        fields = ['id', 'module', 'title', 'description', 'objectives', 'objectives_list',
                  'content_type', 'file', 'duration_seconds', 'duration_formatted', 
                  'file_size_formatted', 'order', 'is_preview', 'is_locked',
                  'downloadables', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super(ModuleLessonSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class ChapterSerializer(serializers.ModelSerializer):
        """Module serializer (renamed from Chapter for clarity)"""
        module_lessons = ModuleLessonSerializer(many=True, read_only=True)
        total_lessons = serializers.SerializerMethodField()
        
        class Meta:
            model=models.Chapter
            fields=['id','course','title','description','video','remarks','order','module_lessons','total_lessons']
        
        def get_total_lessons(self, obj):
            return obj.total_lessons()
        
        def __init__(self, *args, **kwargs):
            super(ChapterSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2


class ModuleLessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for lesson progress tracking"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = models.ModuleLessonProgress
        fields = ['id', 'student', 'lesson', 'lesson_title', 'is_completed', 
                  'last_position_seconds', 'viewed_at', 'completed_at']


class ModuleProgressSerializer(serializers.ModelSerializer):
    """Serializer for module progress tracking"""
    module_title = serializers.CharField(source='module.title', read_only=True)
    
    class Meta:
        model = models.ModuleProgress
        fields = ['id', 'student', 'module', 'module_title', 'is_completed', 
                  'started_at', 'completed_at']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Student
        fields=['id','fullname','email','password','username','interseted_categories','profile_img']
    def __init__(self, *args, **kwargs):
            super(StudentSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2

class StudentCourseEnrollSerializer(serializers.ModelSerializer):        
        class Meta:
            model=models.StudentCourseEnrollment
            fields='__all__'
        def __init__(self, *args, **kwargs):
            super(StudentCourseEnrollSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2
        
        def create(self, validated_data):
            """Create enrollment and also create CourseProgress record"""
            enrollment = super().create(validated_data)
            
            # Create CourseProgress record for this enrollment
            student = enrollment.student
            course = enrollment.course
            
            # Calculate total lessons from modules
            total_lessons = 0
            for chapter in course.course_chapters.all():
                total_lessons += chapter.module_lessons.count()
            
            # Create or update CourseProgress
            course_progress, created = models.CourseProgress.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'enrollment': enrollment,
                    'total_chapters': total_lessons,
                    'completed_chapters': 0,
                    'progress_percentage': 0,
                    'is_completed': False
                }
            )
            
            if not created:
                course_progress.enrollment = enrollment
                course_progress.save()
            
            return enrollment
            

class StudentFavoriteCourseSerializer(serializers.ModelSerializer):
        class Meta:
            model=models.StudentFavoriteCourse
            fields=['id','course','student','status']
        def __init__(self, *args, **kwargs):
            super(StudentFavoriteCourseSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2

class CourseRatingSerializer(serializers.ModelSerializer):
        class Meta:
            model=models.CourseRating
            fields=['id','course','student','rating','reviews','review_time']
        def __init__(self, *args, **kwargs):
            super(CourseRatingSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2

class TeacherDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Teacher
        fields=['total_teacher_course','total_teacher_chapters','total_teacher_students']

class StudentDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Student
        fields=['enrolled_courses','favorite_courses']
        def __init__(self, *args, **kwargs):
            super(StudentDashboardSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2


class StudyMaterialSerializer(serializers.ModelSerializer):
        class Meta:
            model=models.StudyMaterial
            fields=['id','course','title','description','upload','remarks']

        def __init__(self, *args, **kwargs):
            super(StudyMaterialSerializer, self).__init__(*args, **kwargs)
            request = self.context.get('request')
            if request and request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
                print('Method is POST')
                self.Meta.depth = 0
                print(self.Meta.depth)
            else:
                print(f"Method is - {request.method}")
                self.Meta.depth = 2

class FaqSerializer(serializers.ModelSerializer):
        class Meta:
            model=models.Faq
            fields=['question','answer']

class FlatPageSerializer(serializers.ModelSerializer):
    class Meta :
        model=FlatPage
        fields=['id','title','content','url']

# ==================== ADMIN DASHBOARD SERIALIZERS ====================

class AdminSerializer(serializers.ModelSerializer):
    total_managed_schools = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = models.Admin
        fields = ['id', 'full_name', 'email', 'password', 'role', 'profile_img', 
                  'phone', 'is_active', 'created_at', 'updated_at', 'last_login',
                  'total_managed_schools']
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_img': {'required': False, 'allow_null': True}
        }

    def __init__(self, *args, **kwargs):
        super(AdminSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1
    
    def update(self, instance, validated_data):
        # Don't update password through the profile endpoint
        validated_data.pop('password', None)
        return super().update(instance, validated_data)


class AdminDashboardSerializer(serializers.ModelSerializer):
    total_managed_schools = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = models.Admin
        fields = ['id', 'full_name', 'email', 'role', 'profile_img', 
                  'total_managed_schools', 'last_login']


class SchoolSerializer(serializers.ModelSerializer):
    total_teachers = serializers.IntegerField(read_only=True)
    total_students = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = models.School
        fields = ['id', 'name', 'email', 'phone', 'address', 'city', 'state', 
                  'country', 'logo', 'website', 'admin', 'status', 'max_teachers',
                  'max_students', 'max_courses', 'created_at', 'updated_at',
                  'total_teachers', 'total_students', 'total_courses']

    def __init__(self, *args, **kwargs):
        super(SchoolSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class SchoolTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolTeacher
        fields = ['id', 'school', 'teacher', 'is_active', 'joined_at']

    def __init__(self, *args, **kwargs):
        super(SchoolTeacherSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 2


class SchoolStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolStudent
        fields = ['id', 'school', 'student', 'is_active', 'joined_at']

    def __init__(self, *args, **kwargs):
        super(SchoolStudentSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 2


class SchoolCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolCourse
        fields = ['id', 'school', 'course', 'is_featured', 'added_at']

    def __init__(self, *args, **kwargs):
        super(SchoolCourseSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 2


class SubscriptionSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = models.Subscription
        fields = ['id', 'school', 'plan', 'status', 'price', 'start_date', 
                  'end_date', 'auto_renew', 'created_at', 'is_valid']

    def __init__(self, *args, **kwargs):
        super(SubscriptionSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ActivityLog
        fields = ['id', 'admin', 'teacher', 'student', 'action', 'model_name',
                  'object_id', 'description', 'ip_address', 'user_agent', 'created_at']

    def __init__(self, *args, **kwargs):
        super(ActivityLogSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SystemSettings
        fields = ['id', 'site_name', 'site_logo', 'favicon', 'contact_email',
                  'contact_phone', 'address', 'maintenance_mode', 'allow_registration',
                  'default_language', 'timezone', 'updated_at']


class AdminStatsSerializer(serializers.Serializer):
    """Serializer for admin dashboard statistics"""
    total_schools = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    recent_enrollments = serializers.ListField()
    popular_courses = serializers.ListField()
    monthly_stats = serializers.DictField()


# ==================== ENHANCED STUDENT DASHBOARD SERIALIZERS ====================


class WeeklyGoalSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = models.WeeklyGoal
        fields = ['id', 'student', 'goal_type', 'target_value', 'current_value',
                  'week_start', 'week_end', 'is_achieved', 'progress_percentage', 'created_at']

    def __init__(self, *args, **kwargs):
        super(WeeklyGoalSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LessonProgress
        fields = ['id', 'student', 'chapter', 'course', 'is_completed', 
                  'progress_percentage', 'time_spent_seconds', 'last_position_seconds',
                  'started_at', 'completed_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super(LessonProgressSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 2


class CourseProgressSerializer(serializers.ModelSerializer):
    time_spent_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = models.CourseProgress
        fields = ['id', 'student', 'course', 'enrollment', 'total_chapters', 
                  'completed_chapters', 'progress_percentage', 'total_time_spent_seconds',
                  'time_spent_formatted', 'is_completed', 'started_at', 'completed_at', 'last_accessed']

    def get_time_spent_formatted(self, obj):
        hours = obj.total_time_spent_seconds // 3600
        minutes = (obj.total_time_spent_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def __init__(self, *args, **kwargs):
        super(CourseProgressSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 2


class DailyLearningActivitySerializer(serializers.ModelSerializer):
    time_in_minutes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = models.DailyLearningActivity
        fields = ['id', 'student', 'date', 'total_time_seconds', 'time_in_minutes',
                  'lessons_completed', 'quizzes_attempted', 'courses_accessed']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Achievement
        fields = ['id', 'name', 'description', 'icon', 'achievement_type',
                  'requirement_value', 'points', 'is_active']


class StudentAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAchievement
        fields = ['id', 'student', 'achievement', 'earned_at']

    def __init__(self, *args, **kwargs):
        super(StudentAchievementSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 2


class EnhancedStudentDashboardSerializer(serializers.Serializer):
    """Comprehensive serializer for enhanced student dashboard"""
    # Basic stats
    enrolled_courses = serializers.IntegerField()
    favorite_courses = serializers.IntegerField()
    
    # Enhanced stats
    total_learning_time_seconds = serializers.IntegerField()
    total_learning_time_formatted = serializers.CharField()
    courses_completed = serializers.IntegerField()
    courses_in_progress = serializers.IntegerField()
    overall_progress_percentage = serializers.IntegerField()
    
    # Weekly goal
    weekly_goal = serializers.DictField()
    
    # Recent activity
    recent_courses = serializers.ListField()
    recent_achievements = serializers.ListField()
    
    # Learning path progress
    active_learning_paths = serializers.ListField()
    
    # Activity chart data (last 7 days)
    activity_chart_data = serializers.ListField()


# ==================== ENHANCED TEACHER DASHBOARD SERIALIZERS ====================

class TeacherStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.fullname', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    student_profile_img = serializers.ImageField(source='student.profile_img', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = models.TeacherStudent
        fields = ['id', 'teacher', 'student', 'student_name', 'student_email', 
                  'student_profile_img', 'instrument', 'level', 'status', 
                  'progress_percentage', 'last_active', 'time_ago', 'notes', 'assigned_at']

    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.last_active
        
        if diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=2):
            return "1 day ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} days ago"
        else:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"

    def __init__(self, *args, **kwargs):
        super(TeacherStudentSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class TeacherSessionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.fullname', read_only=True)
    student_profile_img = serializers.ImageField(source='student.profile_img', read_only=True)
    formatted_time = serializers.SerializerMethodField()
    
    class Meta:
        model = models.TeacherSession
        fields = ['id', 'teacher', 'student', 'student_name', 'student_profile_img',
                  'title', 'description', 'scheduled_date', 'scheduled_time', 
                  'formatted_time', 'duration_minutes', 'status', 'meeting_link', 
                  'notes', 'created_at', 'updated_at']

    def get_formatted_time(self, obj):
        return obj.scheduled_time.strftime("%H:%M")

    def __init__(self, *args, **kwargs):
        super(TeacherSessionSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class TeacherActivitySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.fullname', read_only=True)
    student_profile_img = serializers.ImageField(source='student.profile_img', read_only=True)
    time_ago = serializers.CharField(read_only=True)
    icon_type = serializers.SerializerMethodField()
    
    class Meta:
        model = models.TeacherActivity
        fields = ['id', 'teacher', 'student', 'student_name', 'student_profile_img',
                  'activity_type', 'target_name', 'target_id', 'target_type',
                  'description', 'time_ago', 'icon_type', 'created_at']

    def get_icon_type(self, obj):
        icon_map = {
            'lesson_completed': 'check',
            'course_started': 'play',
            'comment_added': 'comment',
            'material_downloaded': 'download',
            'session_attended': 'calendar',
        }
        return icon_map.get(obj.activity_type, 'default')


class LessonSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.title', read_only=True)
    duration_formatted = serializers.CharField(read_only=True)
    materials_count = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Lesson
        fields = ['id', 'teacher', 'category', 'category_name', 'title', 
                  'description', 'featured_img', 'difficulty', 'duration_minutes',
                  'duration_formatted', 'module_count', 'materials_count',
                  'is_published', 'created_at', 'updated_at']

    def get_materials_count(self, obj):
        return obj.materials.count()

    def __init__(self, *args, **kwargs):
        super(LessonSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class LessonMaterialSerializer(serializers.ModelSerializer):
    file_size_formatted = serializers.CharField(read_only=True)
    
    class Meta:
        model = models.LessonMaterial
        fields = ['id', 'lesson', 'title', 'material_type', 'file', 
                  'file_size', 'file_size_formatted', 'duration_seconds', 
                  'order', 'created_at']


class TeacherDashboardMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TeacherDashboardMetrics
        fields = ['total_students', 'active_lessons', 'completion_rate',
                  'students_change_percent', 'lessons_change_percent', 
                  'completion_change_percent', 'last_calculated']


class TeacherOverviewSerializer(serializers.Serializer):
    """Comprehensive serializer for teacher dashboard overview"""
    # Teacher info
    teacher_id = serializers.IntegerField()
    teacher_name = serializers.CharField()
    teacher_profile_img = serializers.CharField()
    
    # Metrics
    total_students = serializers.IntegerField()
    active_lessons = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    
    # Trends
    students_trend = serializers.FloatField()
    students_trend_direction = serializers.CharField()
    lessons_trend = serializers.FloatField()
    lessons_trend_direction = serializers.CharField()
    completion_trend = serializers.FloatField()
    completion_trend_direction = serializers.CharField()
    
    # Recent activity (last 10)
    recent_activities = TeacherActivitySerializer(many=True)
    
    # Upcoming sessions (next 5)
    upcoming_sessions = TeacherSessionSerializer(many=True)