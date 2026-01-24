#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_api.settings')
django.setup()

from main import models
from django.utils import timezone
from django.db.models import Sum
from datetime import date, timedelta

# Get the student
student_id = 67  # Sebastian Young
student = models.Student.objects.get(pk=student_id)

# Get current week
today = date.today()
week_start = today - timedelta(days=today.weekday())
week_end = week_start + timedelta(days=6)

print("=" * 60)
print(f"Student: {student.fullname} (ID: {student_id})")
print("=" * 60)
print(f"\nWeek: {week_start} to {week_end}")
print(f"Today: {today}")

# Check completed lessons this week
completed_lessons = models.LessonProgress.objects.filter(
    student=student,
    completed_at__date__gte=week_start,
    completed_at__date__lte=week_end
).count()

# Check completed courses this week
completed_courses = models.CourseProgress.objects.filter(
    student=student,
    completed_at__date__gte=week_start,
    completed_at__date__lte=week_end,
    is_completed=True
).count()

# Check total completed courses (for fallback)
total_completed_courses = models.CourseProgress.objects.filter(
    student=student,
    is_completed=True
).count()

# Check time spent this week
total_time_seconds = models.LessonProgress.objects.filter(
    student=student,
    updated_at__date__gte=week_start,
    updated_at__date__lte=week_end
).aggregate(total=Sum('time_spent_seconds'))['total'] or 0
total_time_minutes = total_time_seconds // 60

print("\n📊 Progress This Week:")
print(f"  ✓ Completed Lessons: {completed_lessons}")
print(f"  ✓ Completed Courses: {completed_courses}")
print(f"  ✓ Study Time (Minutes): {total_time_minutes}")
print(f"\n📚 Total Progress (All Time):")
print(f"  ✓ Total Completed Courses: {total_completed_courses}")

# Get or create weekly goal
goal, created = models.WeeklyGoal.objects.update_or_create(
    student=student,
    week_start=week_start,
    week_end=week_end,
    defaults={
        'goal_type': 'lessons',
        'target_value': 5
    }
)

print(f"\n🎯 Weekly Goal:")
print(f"  Type: {goal.goal_type}")
print(f"  Target: {goal.target_value}")
print(f"  Current Value (Before Update): {goal.current_value}")

# Update current value
goal.update_current_value()

print(f"  Current Value (After Update): {goal.current_value}")
print(f"  Progress: {goal.progress_percentage()}%")
print(f"  Achieved: {goal.is_achieved}")

print("\n" + "=" * 60)
