from django.db import models
from django.core import serializers

class Teacher(models.Model):
    full_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100,blank=True,null=True)
    qualification=models.CharField(max_length=500)
    mobile_no=models.CharField(max_length=20)
    profile_img=models.ImageField(upload_to='teacher_profile_imgs/',null=True)
    skills=models.CharField(max_length=20,null=True)

    face_url=models.URLField(null=True)
    insta_url=models.URLField(null=True)
    twit_url=models.URLField(null=True)
    web_url=models.URLField(null=True)
    you_url=models.URLField(null=True)

    class Meta:
        verbose_name_plural="1. Teacher"

    def skill_list(self):
        skill_list=self.skills.split(',')
        return skill_list

    def total_teacher_course(self):
        total_course=Course.objects.filter(teacher=self).count()
        return total_course

    def total_teacher_chapters(self):
        total_chapters=Chapter.objects.filter(course__teacher=self).count()
        return total_chapters

    def total_teacher_students(self):
        total_students=StudentCourseEnrollment.objects.filter(course__teacher=self).count()
        return total_students 

class CourseCategory(models.Model):
    title=models.CharField(max_length=100)
    description=models.TextField()

    class Meta:
        verbose_name_plural="2. Course Categories"

    def total_courses(self):
        return Course.objects.filter(category=self).count()

    def __str__(self) :
        return self.title

class Course(models.Model):
    category=models.ForeignKey(CourseCategory,on_delete=models.CASCADE, related_name='category_courses')
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE, related_name='teacher_courses')
    title=models.CharField(max_length=150)
    description=models.TextField()
    featured_img=models.ImageField(upload_to='course_imgs/',null=True)
    techs=models.TextField(null=True)
    course_views=models.BigIntegerField(default=0)

    class Meta:
        verbose_name_plural="3. Courses"

    def related_videos(self):
        related_videos=Course.objects.filter(techs__icontains=self.techs).exclude(id=self.id)
        return serializers.serialize('json',related_videos)

    def teach_list(self):
        teach_list=self.techs.split(',')
        return teach_list

    def total_enrolled_students(self):
        total_enrolled_students=StudentCourseEnrollment.objects.filter(course=self).count()
        return total_enrolled_students

    def course_rating(self):
        course_rating=CourseRating.objects.filter(course=self).aggregate(avg_rating=models.Avg('rating'))
        return course_rating['avg_rating']
    
    def __str__(self) :
        return self.title

class Chapter(models.Model):
    """Module - renamed from Chapter for clarity. Contains lessons."""
    course=models.ForeignKey(Course,null=True,on_delete=models.CASCADE,related_name='course_chapters')
    title=models.CharField(max_length=150,null=True)
    description=models.TextField()
    video=models.FileField(upload_to='chapter_videos/',null=True,blank=True)
    remarks=models.TextField(null=True,blank=True)
    order=models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural="4. Modules"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - {self.title}" if self.course else self.title

    def total_lessons(self):
        return self.module_lessons.count()


class ModuleLesson(models.Model):
    """Individual lesson content within a Module (Chapter)"""
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('pdf', 'PDF Document'),
        ('image', 'Image'),
    ]
    
    module = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='module_lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    objectives = models.TextField(blank=True, null=True, help_text="What students will learn in this lesson (one per line)")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='video')
    file = models.FileField(upload_to='lesson_content/')
    duration_seconds = models.IntegerField(default=0)  # For video/audio
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Allow non-enrolled users to preview this lesson")
    is_locked = models.BooleanField(default=True, help_text="Lesson locked until previous lessons completed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "4b. Module Lessons"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    @property
    def duration_formatted(self):
        """Get formatted duration for video/audio"""
        if self.duration_seconds <= 0:
            return "0:00"
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def file_size_formatted(self):
        """Get human-readable file size"""
        try:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Unknown"

    @property
    def objectives_list(self):
        """Return objectives as a list"""
        if not self.objectives:
            return []
        return [obj.strip() for obj in self.objectives.split('\n') if obj.strip()]


class LessonDownloadable(models.Model):
    """Downloadable resources for a lesson (PDFs, audio files, etc.)"""
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('sheet_music', 'Sheet Music'),
        ('audio_slow', 'Audio - Slow Version'),
        ('audio_fast', 'Audio - Fast Version'),
        ('audio_playalong', 'Audio - Play Along'),
        ('worksheet', 'Worksheet'),
        ('other', 'Other'),
    ]
    
    lesson = models.ForeignKey(ModuleLesson, on_delete=models.CASCADE, related_name='downloadables')
    title = models.CharField(max_length=200)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='pdf')
    file = models.FileField(upload_to='lesson_downloadables/')
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "4b2. Lesson Downloadables"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    @property
    def file_size(self):
        """Get file size in bytes"""
        try:
            return self.file.size
        except:
            return 0

    @property
    def file_size_formatted(self):
        """Get human-readable file size"""
        try:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Unknown"

    @property
    def file_extension(self):
        """Get file extension"""
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return "FILE"

    def get_file_type_icon(self):
        """Return icon class based on file type"""
        icons = {
            'pdf': 'bi-file-pdf-fill',
            'sheet_music': 'bi-music-note-list',
            'audio_slow': 'bi-soundwave',
            'audio_fast': 'bi-lightning-fill',
            'audio_playalong': 'bi-headphones',
            'worksheet': 'bi-file-earmark-text-fill',
            'other': 'bi-file-earmark-fill',
        }
        return icons.get(self.file_type, 'bi-file-earmark-fill')


class ModuleLessonProgress(models.Model):
    """Tracks individual lesson progress within a module"""
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='module_lesson_progress')
    lesson = models.ForeignKey(ModuleLesson, on_delete=models.CASCADE, related_name='student_progress')
    is_completed = models.BooleanField(default=False)
    last_position_seconds = models.IntegerField(default=0)  # For video/audio resume
    viewed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "4c. Module Lesson Progress"
        unique_together = ['student', 'lesson']

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.student.fullname} - {self.lesson.title} - {status}"


class ModuleProgress(models.Model):
    """Tracks module (chapter) completion for a student"""
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='student_module_progress')
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "4d. Module Progress"
        unique_together = ['student', 'module']

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.student.fullname} - {self.module.title} - {status}"

    def check_completion(self):
        """Mark module as complete if all lessons are completed"""
        from django.utils import timezone
        total_lessons = self.module.module_lessons.count()
        if total_lessons == 0:
            return
        completed_lessons = ModuleLessonProgress.objects.filter(
            student=self.student,
            lesson__module=self.module,
            is_completed=True
        ).count()
        if completed_lessons >= total_lessons:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()


class Student(models.Model):
    fullname=models.CharField(max_length=100)
    email=models.CharField(max_length=100,unique=True)
    password=models.CharField(max_length=100,null=True,blank=True)
    username=models.CharField(max_length=500)
    interseted_categories=models.TextField()
    profile_img=models.ImageField(upload_to='student_profile_imgs/',null=True)

    def __str__(self) :
        return self.fullname

    def enrolled_courses(self):
        enrolled_courses=StudentCourseEnrollment.objects.filter(student=self).count()
        return enrolled_courses

    def favorite_courses(self):
        favorite_courses=StudentFavoriteCourse.objects.filter(student=self).count()
        return favorite_courses

    class Meta:
        verbose_name_plural="5. Students"

class StudentCourseEnrollment(models.Model):
    course=models.ForeignKey(Course,null=True,on_delete=models.CASCADE,related_name='enrolled_courses')
    student=models.ForeignKey(Student,null=True,on_delete=models.CASCADE,related_name='enrolled_student')
    enrolled_time=models.DateTimeField(auto_now_add=True)

    class Meta:
         verbose_name_plural="6. Enrolled Courses"

    def __str__(self) :
        return f"{self.course}-{self.student}"

class CourseRating(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=True)
    student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True)
    rating=models.PositiveBigIntegerField(default=0)
    reviews=models.TextField(null=True)
    review_time=models.DateTimeField(auto_now_add=True)

    class Meta:
         verbose_name_plural="7. Course Ratings"

    def __str__(self):
        return f"{self.course}-{self.student}-{self.rating}"

class StudentFavoriteCourse(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    status=models.BooleanField(default=False)

    class Meta:
         verbose_name_plural="8. Student Favorite Course"

class StudyMaterial(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    title=models.CharField(max_length=150)
    description=models.TextField()
    upload=models.FileField(upload_to='study_materials/',null=True)
    remarks=models.TextField(null=True)

    class Meta:
         verbose_name_plural="15. Course Materials"

class Faq(models.Model):
    question=models.CharField(max_length=300)
    answer=models.TextField()

    class Meta:
         verbose_name_plural="16. FAQ "


# ==================== ADMIN DASHBOARD MODELS ====================

class Admin(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('school_admin', 'School Admin'),
        ('content_admin', 'Content Admin'),
        ('support_admin', 'Support Admin'),
    ]
    
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='school_admin')
    profile_img = models.ImageField(upload_to='admin_profile_imgs/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "18. Admins"

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    def total_managed_schools(self):
        return School.objects.filter(admin=self).count()


class School(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, default='India')
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_schools')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    max_teachers = models.IntegerField(default=10)
    max_students = models.IntegerField(default=100)
    max_courses = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "19. Schools"

    def __str__(self):
        return self.name

    def total_teachers(self):
        return SchoolTeacher.objects.filter(school=self).count()

    def total_students(self):
        return SchoolStudent.objects.filter(school=self).count()

    def total_courses(self):
        return SchoolCourse.objects.filter(school=self).count()


class SchoolTeacher(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_teachers')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_schools')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "20. School Teachers"
        unique_together = ['school', 'teacher']


class SchoolStudent(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_students')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_schools')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "21. School Students"
        unique_together = ['school', 'student']


class SchoolCourse(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_schools')
    is_featured = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "22. School Courses"
        unique_together = ['school', 'course']


class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_date = models.DateField()
    end_date = models.DateField()
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "23. Subscriptions"

    def __str__(self):
        return f"{self.school.name} - {self.plan}"

    def is_valid(self):
        from datetime import date
        return self.status == 'active' and self.end_date >= date.today()


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "24. Activity Logs"
        ordering = ['-created_at']

    def __str__(self):
        user = self.admin or self.teacher or self.student
        return f"{user} - {self.action} - {self.created_at}"


class SystemSettings(models.Model):
    site_name = models.CharField(max_length=200, default='EduLearning')
    site_logo = models.ImageField(upload_to='system/', null=True, blank=True)
    favicon = models.ImageField(upload_to='system/', null=True, blank=True)
    contact_email = models.EmailField(default='admin@edulearning.com')
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    maintenance_mode = models.BooleanField(default=False)
    allow_registration = models.BooleanField(default=True)
    default_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "25. System Settings"

    def __str__(self):
        return self.site_name



# ==================== ENHANCED STUDENT DASHBOARD MODELS ====================



class WeeklyGoal(models.Model):
    """Student's weekly learning goals"""
    GOAL_TYPE_CHOICES = [
        ('lessons', 'Complete Lessons'),
        ('minutes', 'Study Minutes'),
        ('courses', 'Complete Courses'),
        ('quizzes', 'Pass Quizzes'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='weekly_goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='lessons')
    target_value = models.IntegerField(default=5)
    current_value = models.IntegerField(default=0)
    week_start = models.DateField()
    week_end = models.DateField()
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "29. Weekly Goals"
        ordering = ['-week_start']

    def __str__(self):
        return f"{self.student.fullname} - {self.goal_type}: {self.current_value}/{self.target_value}"

    def calculate_current_value(self):
        """Calculate current value based on actual progress in this week"""
        from django.db.models import Sum, Q
        from django.utils import timezone
        
        if self.goal_type == 'lessons':
            # Count completed lessons this week (by completed_at date)
            completed_lessons = LessonProgress.objects.filter(
                student=self.student,
                completed_at__date__gte=self.week_start,
                completed_at__date__lte=self.week_end
            ).count()
            
            # If no lessons completed by exact date, count lessons updated/worked on this week
            if completed_lessons == 0:
                completed_lessons = LessonProgress.objects.filter(
                    student=self.student,
                    updated_at__date__gte=self.week_start,
                    updated_at__date__lte=self.week_end,
                    is_completed=True
                ).count()
            
            # If still no lessons (no LessonProgress records), count chapters in courses 
            # that were COMPLETED this week (use completed_at timestamp)
            if completed_lessons == 0:
                completed_courses_this_week = CourseProgress.objects.filter(
                    student=self.student,
                    is_completed=True,
                    completed_at__date__gte=self.week_start,
                    completed_at__date__lte=self.week_end
                )
                # Count all chapters from courses completed THIS WEEK
                for cp in completed_courses_this_week:
                    completed_lessons += cp.total_chapters
            
            return completed_lessons
        
        elif self.goal_type == 'minutes':
            # Calculate total study minutes this week
            total_seconds = LessonProgress.objects.filter(
                student=self.student,
                updated_at__date__gte=self.week_start,
                updated_at__date__lte=self.week_end
            ).aggregate(total=Sum('time_spent_seconds'))['total'] or 0
            
            # If no lesson progress, check CourseProgress for this week
            if total_seconds == 0:
                total_seconds = CourseProgress.objects.filter(
                    student=self.student,
                    last_accessed__date__gte=self.week_start,
                    last_accessed__date__lte=self.week_end
                ).aggregate(total=Sum('total_time_spent_seconds'))['total'] or 0
            
            return total_seconds // 60  # Convert to minutes
        
        elif self.goal_type == 'courses':
            # Count completed courses this week
            completed_courses = CourseProgress.objects.filter(
                student=self.student,
                completed_at__date__gte=self.week_start,
                completed_at__date__lte=self.week_end,
                is_completed=True
            ).count()
            return completed_courses
        
        elif self.goal_type == 'quizzes':
            # Count passed quizzes this week
            from main.models import AttemptQuiz
            passed_quizzes = AttemptQuiz.objects.filter(
                student=self.student,
                created_at__date__gte=self.week_start,
                created_at__date__lte=self.week_end,
                is_passed=True
            ).values('quiz').distinct().count()
            return passed_quizzes
        
        return 0

    def update_current_value(self):
        """Update and save the current value based on actual progress"""
        self.current_value = self.calculate_current_value()
        self.check_achievement()
        self.save()

    def check_achievement(self):
        if self.current_value >= self.target_value:
            self.is_achieved = True
            self.save()
        return self.is_achieved

    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, int((self.current_value / self.target_value) * 100))


class LessonProgress(models.Model):
    """Tracks individual lesson/chapter completion for a student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lesson_progress')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='student_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lesson_progress')
    is_completed = models.BooleanField(default=False)
    progress_percentage = models.IntegerField(default=0)  # 0-100
    time_spent_seconds = models.IntegerField(default=0)
    last_position_seconds = models.IntegerField(default=0)  # For video resume
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "30. Lesson Progress"
        unique_together = ['student', 'chapter']

    def __str__(self):
        return f"{self.student.fullname} - {self.chapter.title} - {self.progress_percentage}%"


class CourseProgress(models.Model):
    """Aggregated course progress for a student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_course_progress')
    enrollment = models.OneToOneField(StudentCourseEnrollment, on_delete=models.CASCADE, related_name='progress', null=True)
    total_chapters = models.IntegerField(default=0)
    completed_chapters = models.IntegerField(default=0)
    progress_percentage = models.IntegerField(default=0)
    total_time_spent_seconds = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "31. Course Progress"
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.fullname} - {self.course.title} - {self.progress_percentage}%"

    def update_progress(self):
        from django.utils import timezone
        total = self.course.course_chapters.count()
        completed = LessonProgress.objects.filter(
            student=self.student,
            course=self.course,
            is_completed=True
        ).count()
        
        self.total_chapters = total
        self.completed_chapters = completed
        self.progress_percentage = int((completed / total) * 100) if total > 0 else 0
        
        # Update total time spent
        total_time = LessonProgress.objects.filter(
            student=self.student,
            course=self.course
        ).aggregate(total=models.Sum('time_spent_seconds'))['total'] or 0
        self.total_time_spent_seconds = total_time
        
        if self.progress_percentage == 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        
        self.save()


class DailyLearningActivity(models.Model):
    """Tracks daily learning time and activity"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField()
    total_time_seconds = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    quizzes_attempted = models.IntegerField(default=0)
    courses_accessed = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "32. Daily Learning Activities"
        unique_together = ['student', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.fullname} - {self.date} - {self.total_time_seconds // 60} mins"

    @property
    def time_in_minutes(self):
        return self.total_time_seconds // 60


class Achievement(models.Model):
    """Gamification achievements/badges"""
    ACHIEVEMENT_TYPE_CHOICES = [
        ('completion', 'Course Completion'),
        ('quiz_master', 'Quiz Master'),
        ('time_spent', 'Time Spent'),
        ('first_steps', 'First Steps'),
        ('social', 'Social Achievement'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/', null=True, blank=True)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES)
    requirement_value = models.IntegerField(default=1)  # e.g., 1 course for completion
    points = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "36. Achievements"

    def __str__(self):
        return self.name


class StudentAchievement(models.Model):
    """Achievements earned by students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='earned_by')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "37. Student Achievements"
        unique_together = ['student', 'achievement']

    def __str__(self):
        return f"{self.student.fullname} - {self.achievement.name}"


# ==================== ENHANCED TEACHER DASHBOARD MODELS ====================

class TeacherStudent(models.Model):
    """Direct teacher-student relationship for the new dashboard"""
    INSTRUMENT_CHOICES = [
        ('piano', 'Piano'),
        ('guitar', 'Guitar'),
        ('violin', 'Violin'),
        ('voice', 'Voice'),
        ('drums', 'Drums'),
        ('flute', 'Flute'),
        ('saxophone', 'Saxophone'),
        ('other', 'Other'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('warning', 'Warning'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assigned_students')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assigned_teachers')
    instrument = models.CharField(max_length=20, choices=INSTRUMENT_CHOICES, default='piano')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress_percentage = models.IntegerField(default=0)
    last_active = models.DateTimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "39. Teacher Students"
        unique_together = ['teacher', 'student']
        ordering = ['-last_active']

    def __str__(self):
        return f"{self.teacher.full_name} - {self.student.fullname}"

    def update_status(self):
        """Auto-update status based on last activity"""
        from datetime import timedelta
        from django.utils import timezone
        
        now = timezone.now()
        days_inactive = (now - self.last_active).days
        
        if days_inactive > 14:
            self.status = 'inactive'
        elif days_inactive > 7:
            self.status = 'warning'
        else:
            self.status = 'active'
        self.save()


class TeacherSession(models.Model):
    """Teaching sessions/appointments for teacher dashboard"""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teaching_sessions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='learning_sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    meeting_link = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "40. Teacher Sessions"
        ordering = ['scheduled_date', 'scheduled_time']

    def __str__(self):
        return f"{self.teacher.full_name} - {self.student.fullname} - {self.scheduled_date}"


class TeacherActivity(models.Model):
    """Activity feed for teacher dashboard"""
    ACTIVITY_TYPES = [
        ('lesson_completed', 'Completed Lesson'),
        ('assignment_submitted', 'Submitted Assignment'),
        ('course_started', 'Started Course'),
        ('comment_added', 'Added Comment'),
        ('material_downloaded', 'Downloaded Material'),
        ('session_attended', 'Attended Session'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='activity_feed')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='teacher_activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    target_name = models.CharField(max_length=200)  # Name of lesson/course/assignment
    target_id = models.IntegerField(null=True, blank=True)
    target_type = models.CharField(max_length=50, null=True, blank=True)  # 'course', 'chapter', 'quiz', etc.
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "41. Teacher Activities"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.fullname} - {self.activity_type} - {self.target_name}"

    @property
    def time_ago(self):
        """Get human-readable time ago"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - self.created_at
        
        if diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=2):
            return "Yesterday"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            return self.created_at.strftime("%b %d, %Y")


class Lesson(models.Model):
    """Enhanced lesson model for lesson library"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='lessons')
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    featured_img = models.ImageField(upload_to='lesson_imgs/', null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_minutes = models.IntegerField(default=0)  # Total duration in minutes
    module_count = models.IntegerField(default=1)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "42. Lessons"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def duration_formatted(self):
        """Get formatted duration"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class LessonMaterial(models.Model):
    """Materials/files for lessons"""
    MATERIAL_TYPES = [
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('pdf', 'PDF Document'),
        ('image', 'Image'),
        ('other', 'Other'),
    ]
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='video')
    file = models.FileField(upload_to='lesson_materials/')
    file_size = models.BigIntegerField(default=0)  # Size in bytes
    duration_seconds = models.IntegerField(default=0)  # For video/audio
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "43. Lesson Materials"
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    @property
    def file_size_formatted(self):
        """Get human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class TeacherDashboardMetrics(models.Model):
    """Cached metrics for teacher dashboard performance"""
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='dashboard_metrics')
    total_students = models.IntegerField(default=0)
    active_lessons = models.IntegerField(default=0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Trend data
    students_change_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    lessons_change_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    completion_change_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    last_calculated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "45. Teacher Dashboard Metrics"

    def __str__(self):
        return f"{self.teacher.full_name} - Metrics"

    def calculate_metrics(self):
        """Recalculate all metrics"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg
        
        now = timezone.now()
        last_month = now - timedelta(days=30)
        last_week = now - timedelta(days=7)
        
        # Total students (via TeacherStudent relationship)
        current_students = TeacherStudent.objects.filter(teacher=self.teacher).count()
        previous_students = TeacherStudent.objects.filter(
            teacher=self.teacher,
            assigned_at__lte=last_month
        ).count()
        
        self.total_students = current_students
        if previous_students > 0:
            self.students_change_percent = ((current_students - previous_students) / previous_students) * 100
        else:
            self.students_change_percent = 100 if current_students > 0 else 0
        
        # Active lessons
        current_lessons = Lesson.objects.filter(teacher=self.teacher, is_published=True).count()
        new_lessons_this_week = Lesson.objects.filter(
            teacher=self.teacher,
            created_at__gte=last_week
        ).count()
        
        self.active_lessons = current_lessons
        if current_lessons > 0:
            self.lessons_change_percent = (new_lessons_this_week / current_lessons) * 100
        else:
            self.lessons_change_percent = 0
        
        # Completion rate
        total_assignments = LessonAssignment.objects.filter(teacher=self.teacher).count()
        completed_assignments = LessonAssignment.objects.filter(
            teacher=self.teacher,
            is_completed=True
        ).count()
        
        if total_assignments > 0:
            self.completion_rate = (completed_assignments / total_assignments) * 100
        else:
            self.completion_rate = 0
        
        # Previous completion rate for trend
        prev_total = LessonAssignment.objects.filter(
            teacher=self.teacher,
            assigned_at__lte=last_month
        ).count()
        prev_completed = LessonAssignment.objects.filter(
            teacher=self.teacher,
            is_completed=True,
            completed_at__lte=last_month
        ).count()
        
        if prev_total > 0:
            prev_rate = (prev_completed / prev_total) * 100
            self.completion_change_percent = float(self.completion_rate) - prev_rate
        else:
            self.completion_change_percent = 0
        
        self.save()