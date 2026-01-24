#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_api.settings')
django.setup()

from main.models import Student, LessonProgress, CourseProgress, StudentAchievement, Achievement
from django.db.models import Sum

# Find the student Sebastian Young
student = Student.objects.filter(fullname__icontains='sebastian').first()

if student:
    print(f"\n{'='*60}")
    print(f"Student: {student.fullname} (ID: {student.id})")
    print(f"{'='*60}")
    
    # Check lesson progress
    lessons = LessonProgress.objects.filter(student=student)
    print(f"\n📚 Lesson Progress: {lessons.count()} lessons")
    for lesson in lessons:
        print(f"  - {lesson.chapter.title}: {lesson.progress_percentage}% - Completed: {lesson.is_completed}")
    
    # Check course progress
    courses = CourseProgress.objects.filter(student=student)
    print(f"\n🎓 Course Progress: {courses.count()} courses")
    for course in courses:
        print(f"  - {course.course.title}: {course.progress_percentage}% - Completed: {course.is_completed}")
    
    # Check achievements
    achievements = StudentAchievement.objects.filter(student=student)
    print(f"\n🏆 Achievements Earned: {achievements.count()}")
    for ach in achievements:
        print(f"  - {ach.achievement.name} ({ach.achievement.achievement_type}): {ach.earned_at}")
    
    # Manually trigger achievement check
    print(f"\n{'='*60}")
    print("Achievement Check Logic")
    print(f"{'='*60}")
    
    lesson_count = LessonProgress.objects.filter(student=student, is_completed=True).count()
    print(f"\n✓ LessonProgress records: {lesson_count}")
    
    # If no lesson progress records, count completed courses
    if lesson_count == 0:
        lesson_count = CourseProgress.objects.filter(student=student, is_completed=True).count()
        print(f"✓ Using completed courses instead: {lesson_count}")
    
    course_count = CourseProgress.objects.filter(student=student, is_completed=True).count()
    print(f"✓ Courses Completed: {course_count}")
    
    first_steps = Achievement.objects.filter(achievement_type='first_steps', is_active=True)
    print(f"\nAvailable First Steps Achievements:")
    for ach in first_steps:
        print(f"  - {ach.name}: requires {ach.requirement_value} lessons", end="")
        if lesson_count >= ach.requirement_value:
            earned, created = StudentAchievement.objects.get_or_create(student=student, achievement=ach)
            print(f" ✅ EARNED (Created now: {created})")
        else:
            print(f" ⏳ (need {ach.requirement_value - lesson_count} more)")
    
    completion_ach = Achievement.objects.filter(achievement_type='completion', is_active=True)
    print(f"\nAvailable Completion Achievements:")
    for ach in completion_ach:
        print(f"  - {ach.name}: requires {ach.requirement_value} courses", end="")
        if course_count >= ach.requirement_value:
            earned, created = StudentAchievement.objects.get_or_create(student=student, achievement=ach)
            print(f" ✅ EARNED (Created now: {created})")
        else:
            print(f" ⏳ (need {ach.requirement_value - course_count} more)")
    
    print(f"\n{'='*60}")
    print("Updated Achievements")
    print(f"{'='*60}")
    achievements = StudentAchievement.objects.filter(student=student)
    print(f"\nTotal Achievements Earned: {achievements.count()}")
    for ach in achievements:
        print(f"  ✅ {ach.achievement.name} ({ach.achievement.achievement_type})")
else:
    print("Student not found")
