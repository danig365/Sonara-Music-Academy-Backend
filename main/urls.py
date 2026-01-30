from django.urls import path
from . import views

urlpatterns =[
        path('teacher/', views.TeacherList.as_view()),

        path('student/', views.StudentList.as_view()),

        path('teacher/<int:pk>/',views.TeacherDetail.as_view()),
        
        path('teacher-login',views.teacher_login),

        path('teacher/change-password/<int:teacher_id>/',views.teacher_change_password),

        path('student/change-password/<int:student_id>/',views.student_change_password),

        path('teacher/dashboard/<int:pk>/', views.TeacherDashboard.as_view()),

        path('student/dashboard/<int:pk>/', views.StudentDashboard.as_view()),

        path('student-login',views.student_login),

        path('student/<int:pk>/',views.StudentDetail.as_view()),

        path('category/', views.CategoryList.as_view()),

        path('course/', views.CourseList.as_view()),

        path('search-courses/<str:searchstring>', views.CourseList.as_view()),

        path('course/<int:pk>/', views.CourseDetailView.as_view()),

        path('chapter/<int:pk>', views.ChapterDetailView.as_view()),

        path('course-chapters/<int:course_id>', views.CourseChapterList.as_view()),

        path('teacher-course/<int:teacher_id>', views.TeacherCourseList.as_view()),

        path('teacher-course-detail/<int:pk>', views.TeacherCourseDetail.as_view()),

        path('student-enroll-course/', views.StudentEnrollCourseList.as_view()),

        path('fetch-enroll-status/<int:student_id>/<int:course_id>', views.fetch_enroll_status),

        path('fetch-enrolled-courses/<int:student_id>', views.EnrolledStuentList.as_view()),

        path('fetch-enrolled-students/<int:course_id>', views.EnrolledStuentList.as_view()),

        path('fetch-recomemded-coourses/<int:student_id>', views.EnrolledStuentList.as_view()),

        path('fetch-all-enrolled-students/<int:teacher_id>', views.EnrolledStuentList.as_view()),

        path('course-rating/', views.CourseRatingList.as_view()),

        path('popular-courses/', views.CourseRatingList.as_view()),

        path('fetch-rating-status/<int:student_id>/<int:course_id>', views.fetch_rating_status),
        path('fetch-favorite-status/<int:student_id>/<int:course_id>', views.fetch_favorite_status),

        path('student-add-favorte-course/', views.StudentFavoriteCourseList.as_view()),

        path('student-remove-favorite-course/<int:course_id>/<int:student_id>', views.remove_favorite_course),

        path('fetch-favorite-coourses/<int:student_id>', views.StudentFavoriteCourseList.as_view()),

        path('study-material/<int:course_id>', views.StudyMaterialList.as_view()),

        path('study-materials/<int:pk>', views.StudyMaterialView.as_view()),

        path('user/study-material/<int:course_id>', views.StudyMaterialList.as_view()),

        path('update-view/<int:course_id>', views.update_view),

        path('student-test/', views.CourseRatingList.as_view()),

        path('popular-teachers/', views.TeacherList.as_view()),

        path('faq/', views.FaqList.as_view()),

        path('pages/', views.FlatPagesList.as_view()),

        path('pages/<int:pk>/<str:page_slug>', views.FlatPagesDetail.as_view()),

        path('fetch-my-teachers/<int:student_id>', views.MyTeacherList().as_view()),

        # ==================== ADMIN DASHBOARD URLS ====================
        
        # Admin Authentication
        path('admin-user/', views.AdminList.as_view()),
        path('admin-user/<int:pk>/', views.AdminDetail.as_view()),
        path('admin-login', views.admin_login),
        path('admin/change-password/<int:admin_id>/', views.admin_change_password),
        path('admin/dashboard/<int:pk>/', views.AdminDashboard.as_view()),
        path('admin/stats/', views.admin_stats),
        
        # School Management
        path('schools/', views.SchoolList.as_view()),
        path('schools/<int:pk>/', views.SchoolDetail.as_view()),
        path('schools/<int:school_id>/teachers/', views.SchoolTeacherList.as_view()),
        path('school-teachers/<int:pk>/', views.SchoolTeacherDetail.as_view()),
        path('schools/<int:school_id>/students/', views.SchoolStudentList.as_view()),
        path('school-students/<int:pk>/', views.SchoolStudentDetail.as_view()),
        path('schools/<int:school_id>/courses/', views.SchoolCourseList.as_view()),
        path('school-courses/<int:pk>/', views.SchoolCourseDetail.as_view()),
        
        # Activity Logs
        path('activity-logs/', views.ActivityLogList.as_view()),
        
        # System Settings
        path('system-settings/', views.SystemSettingsList.as_view()),
        path('system-settings/<int:pk>/', views.SystemSettingsDetail.as_view()),
        path('get-settings/', views.get_or_create_settings),
        
        # Admin Management of All Users
        path('admin/teachers/', views.AdminTeacherList.as_view()),
        path('admin/toggle-teacher/<int:teacher_id>/', views.admin_toggle_teacher_status),
        path('admin/students/', views.AdminStudentList.as_view()),
        path('admin/courses/', views.AdminCourseList.as_view()),
        path('admin/course/create/', views.AdminCourseCreate.as_view()),
        path('admin/course/<int:pk>/', views.AdminCourseDetail.as_view()),
        path('admin/delete-course/<int:course_id>/', views.admin_delete_course),

        # ==================== ADMIN LESSON MANAGEMENT URLS ====================
        
        # Modules (formerly Chapters)
        path('admin/modules/', views.AdminModuleList.as_view()),
        path('admin/module/<int:pk>/', views.AdminModuleDetail.as_view()),
        path('admin/course/<int:course_id>/modules/', views.AdminCourseModulesWithLessons.as_view()),
        path('admin/course/<int:course_id>/reorder-modules/', views.admin_reorder_modules),
        
        # Module Lessons
        path('admin/module/<int:module_id>/lessons/', views.AdminModuleLessonList.as_view()),
        path('admin/lesson/<int:pk>/', views.AdminModuleLessonDetail.as_view()),
        path('admin/module/<int:module_id>/reorder-lessons/', views.admin_reorder_lessons),
        path('admin/lessons/bulk-delete/', views.admin_bulk_delete_lessons),
        
        # Lesson Downloadables (Admin)
        path('lesson/<int:lesson_id>/downloadables/', views.LessonDownloadableList.as_view()),
        path('downloadable/<int:pk>/', views.LessonDownloadableDetail.as_view()),
        path('downloadable/<int:downloadable_id>/increment/', views.increment_download_count),
        
        # Student Lesson Progress
        path('student/<int:student_id>/course/<int:course_id>/progress/', views.StudentModuleProgress.as_view()),
        path('student/<int:student_id>/course/<int:course_id>/progress-enhanced/', views.StudentModuleProgressEnhanced.as_view()),
        path('student/<int:student_id>/lesson/<int:lesson_id>/complete/', views.mark_lesson_complete),
        path('student/<int:student_id>/lesson/<int:lesson_id>/position/', views.update_lesson_position),
        path('student/<int:student_id>/course/<int:course_id>/lesson/<int:current_lesson_id>/navigation/', views.StudentCourseNavigation.as_view()),
        path('student/<int:student_id>/lesson/<int:lesson_id>/unlock-status/', views.check_lesson_unlock_status),
        path('lesson/<int:lesson_id>/detail/', views.LessonDetailWithDownloadables.as_view()),
        path('lesson/<int:lesson_id>/detail/<int:student_id>/', views.LessonDetailWithDownloadables.as_view()),
        
        # Consolidated Lesson Page Data (replaces 3 separate calls)
        path('student/<int:student_id>/course/<int:course_id>/lesson/<int:lesson_id>/full-page-data/', 
             views.StudentLessonPageData.as_view()),
        path('student/<int:student_id>/course/<int:course_id>/full-page-data/', 
             views.StudentLessonPageData.as_view()),

        # ==================== ENHANCED STUDENT DASHBOARD URLS ====================
        
        # Enhanced Dashboard
        path('student/enhanced-dashboard/<int:student_id>/', views.EnhancedStudentDashboard.as_view()),
        
        # Streak Calendar & Gamification
        path('student/streak-calendar/<int:student_id>/', views.StudentStreakCalendar.as_view()),
        path('student/all-achievements/<int:student_id>/', views.StudentAllAchievements.as_view()),
        
        # Weekly Goals
        path('student/weekly-goals/<int:student_id>/', views.WeeklyGoalList.as_view()),
        path('student/weekly-goal/<int:pk>/', views.WeeklyGoalDetail.as_view()),
        path('student/create-weekly-goal/<int:student_id>/', views.create_weekly_goal),
        
        # Lesson Progress
        path('student/lesson-progress/<int:student_id>/', views.LessonProgressList.as_view()),
        path('student/lesson-progress/<int:student_id>/<int:course_id>/', views.LessonProgressList.as_view()),
        path('student/update-lesson-progress/<int:student_id>/<int:chapter_id>/', views.update_lesson_progress),
        
        # Course Progress
        path('student/course-progress/<int:student_id>/', views.CourseProgressList.as_view()),
        path('student/course-progress/<int:student_id>/<int:course_id>/', views.CourseProgressDetail.as_view()),
        
        # Daily Activity
        path('student/daily-activity/<int:student_id>/', views.DailyActivityList.as_view()),
        
        # Achievements
        path('achievements/', views.AchievementList.as_view()),
        path('student/achievements/<int:student_id>/', views.StudentAchievementList.as_view()),
        path('student/check-achievements/<int:student_id>/', views.check_achievements),
        
        # ==================== ENHANCED TEACHER DASHBOARD URLS ====================
        
        # Teacher Dashboard Overview
        path('teacher/overview/<int:teacher_id>/', views.TeacherOverviewDashboard.as_view()),
        
        # Teacher Students Management
        path('teacher/students/<int:teacher_id>/', views.TeacherStudentList.as_view()),
        path('teacher/student/<int:pk>/', views.TeacherStudentDetail.as_view()),
        path('teacher/students-from-enrollments/<int:teacher_id>/', views.get_teacher_students_from_enrollments),
        
        # Teacher Sessions/Appointments
        path('teacher/sessions/<int:teacher_id>/', views.TeacherSessionList.as_view()),
        path('teacher/session/<int:pk>/', views.TeacherSessionDetail.as_view()),
        
        # Teacher Activity Feed
        path('teacher/activities/<int:teacher_id>/', views.TeacherActivityList.as_view()),
        path('teacher/activity/create/<int:teacher_id>/', views.create_teacher_activity),
        
        # Lesson Library
        path('teacher/lessons/<int:teacher_id>/', views.TeacherLessonList.as_view()),
        path('teacher/lesson/<int:pk>/', views.TeacherLessonDetail.as_view()),
        
        # Lesson Materials
        path('lesson/materials/<int:lesson_id>/', views.LessonMaterialList.as_view()),
        path('lesson/material/<int:pk>/', views.LessonMaterialDetail.as_view()),
        path('lesson/upload-material/<int:lesson_id>/', views.upload_lesson_material),
        
        # Teacher Progress Dashboard
        path('teacher/progress/<int:teacher_id>/', views.TeacherProgressDashboard.as_view()),

        # ==================== SUBSCRIPTION MANAGEMENT URLS ====================
        
        # Subscription Plans
        path('subscription-plans/', views.SubscriptionPlanList.as_view()),
        path('subscription-plan/<int:pk>/', views.SubscriptionPlanDetail.as_view()),
        
        # Subscriptions
        path('subscriptions/', views.SubscriptionList.as_view()),
        path('subscription/create-payment-intent/', views.create_payment_intent),
        path('subscription/<int:subscription_id>/activate/', views.activate_subscription),
        path('subscription/<int:subscription_id>/cancel/', views.cancel_subscription),
        path('subscription/<int:pk>/', views.SubscriptionDetail.as_view()),
        
        # Subscription History
        path('subscription-history/', views.SubscriptionHistoryList.as_view()),
        
        # Admin Stats
        path('admin/subscription-stats/', views.get_admin_subscription_stats),

]