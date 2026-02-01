#!/usr/bin/env python
"""
Generate dummy audit logs data using API endpoints
Tests the audit logging system with realistic data
"""

import os
import sys
import django
import requests
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_api.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Student, Teacher, Course, Chapter, SubscriptionPlan, Subscription

# API Configuration
API_BASE_URL = 'http://127.0.0.1:8000/api'

# Sample data for logging
UPLOAD_TYPES = ['lesson_content', 'student_submission', 'profile_image', 'course_image', 'study_material']
PAYMENT_TYPES = ['subscription_purchase', 'plan_upgrade', 'plan_downgrade', 'renewal', 'refund']
PAYMENT_METHODS = ['stripe', 'paypal', 'credit_card', 'debit_card', 'net_banking']
PAYMENT_STATUSES = ['completed', 'failed', 'pending', 'refunded']
ACCESS_TYPES = ['course_view', 'lesson_view', 'course_enroll', 'course_unenroll', 'download_material', 'lesson_complete']
DENIAL_REASONS = ['teacher_not_in_plan', 'category_not_allowed', 'subscription_expired', 'student_not_enrolled', 'access_restricted']

def log_upload(teacher_id=None, student_id=None, admin_id=None):
    """Log a file upload"""
    user_id = teacher_id or student_id or admin_id
    user_type = 'teacher' if teacher_id else ('student' if student_id else 'admin')
    
    payload = {
        'file_name': f'sample_{random.randint(1000, 9999)}.mp4',
        'file_type': random.choice(['mp4', 'pdf', 'docx', 'jpg', 'zip']),
        'file_size': random.randint(1000000, 500000000),  # 1MB to 500MB
        'upload_type': random.choice(UPLOAD_TYPES),
        f'{user_type}_id': user_id,
        'status': random.choice(['success', 'success', 'success', 'failed', 'pending']),  # More successes
        'ip_address': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
        'error_message': 'Network timeout' if random.random() > 0.8 else None
    }
    
    try:
        response = requests.post(f'{API_BASE_URL}/audit/log-upload/', json=payload)
        if response.status_code in [200, 201]:
            print(f'✓ Upload logged: {payload["file_name"]} ({payload["upload_type"]})')
            return True
        else:
            print(f'✗ Upload log failed: {response.status_code} - {response.text}')
            return False
    except Exception as e:
        print(f'✗ Error logging upload: {str(e)}')
        return False

def log_payment(student_id, plan_id):
    """Log a payment transaction"""
    amount = Decimal(random.choice([99.99, 199.99, 299.99, 499.99, 799.99]))
    tax = amount * Decimal('0.18')  # 18% tax
    discount = amount * Decimal(random.choice([0, 0, 0.1, 0.15])) if random.random() > 0.5 else Decimal(0)
    final_amount = amount + tax - discount
    
    payload = {
        'transaction_id': f'TXN_{random.randint(100000, 999999)}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'student_id': student_id,
        'subscription_plan_id': plan_id,
        'payment_type': random.choice(PAYMENT_TYPES),
        'status': random.choice(PAYMENT_STATUSES),
        'payment_method': random.choice(PAYMENT_METHODS),
        'amount': float(amount),
        'tax_amount': float(tax),
        'discount_amount': float(discount),
        'final_amount': float(final_amount),
        'currency': 'INR',
        'user_email': f'student_{student_id}@edulearning.com',
        'user_ip_address': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
        'receipt_url': f'https://receipts.example.com/{random.randint(100000, 999999)}',
        'invoice_number': f'INV-{datetime.now().strftime("%Y%m%d")}-{random.randint(1000, 9999)}',
    }
    
    try:
        response = requests.post(f'{API_BASE_URL}/audit/log-payment/', json=payload)
        if response.status_code in [200, 201]:
            print(f'✓ Payment logged: {payload["transaction_id"]} - ₹{final_amount} ({payload["payment_type"]})')
            return True
        else:
            print(f'✗ Payment log failed: {response.status_code} - {response.text}')
            return False
    except Exception as e:
        print(f'✗ Error logging payment: {str(e)}')
        return False

def log_access(student_id, course_id=None, lesson_id=None):
    """Log a resource access"""
    access_type = random.choice(ACCESS_TYPES)
    was_allowed = random.random() > 0.15  # 85% allowed, 15% denied
    denial_reason = random.choice(DENIAL_REASONS) if not was_allowed else None
    duration = random.randint(60, 3600) if was_allowed else 0  # 1 min to 1 hour
    
    payload = {
        'student_id': student_id,
        'access_type': access_type,
        'course_id': course_id,
        'lesson_id': lesson_id,
        'was_allowed': was_allowed,
        'denial_reason': denial_reason,
        'duration_seconds': duration,
        'ip_address': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
    }
    
    try:
        response = requests.post(f'{API_BASE_URL}/audit/log-access/', json=payload)
        if response.status_code in [200, 201]:
            status = '✓ Allowed' if was_allowed else f'✗ Denied ({denial_reason})'
            print(f'✓ Access logged: {access_type} - {status}')
            return True
        else:
            print(f'✗ Access log failed: {response.status_code} - {response.text}')
            return False
    except Exception as e:
        print(f'✗ Error logging access: {str(e)}')
        return False

def get_or_create_test_users():
    """Get or create test students and admins"""
    students = []
    teachers = []
    admins = []
    
    # Get or create test students (using custom Student model)
    for i in range(5):
        student, created = Student.objects.get_or_create(
            email=f'teststudent{i+1}@test.com',
            defaults={
                'fullname': f'Student Test {i+1}',
                'username': f'teststudent{i+1}',
                'password': 'hashed_password_here',
                'interseted_categories': 'Technology,Music'
            }
        )
        students.append(student)
        status = 'Created' if created else 'Using'
        print(f'✓ {status} student: {student.fullname} (ID: {student.id})')
    
    # Get or create test teachers
    for i in range(3):
        teacher, created = Teacher.objects.get_or_create(
            email=f'testteacher{i+1}@test.com',
            defaults={
                'full_name': f'Teacher Test {i+1}',
                'qualification': 'M.Tech',
                'mobile_no': f'987654{i:04d}',
                'skills': 'Python,JS'
            }
        )
        teachers.append(teacher)
        status = 'Created' if created else 'Using'
        print(f'✓ {status} teacher: {teacher.full_name} (ID: {teacher.id})')
    
    # Get or create test admins (Django User model)
    for i in range(2):
        admin_user, created = User.objects.get_or_create(
            username=f'testadmin{i+1}',
            defaults={
                'email': f'testadmin{i+1}@test.com',
                'first_name': f'Admin',
                'last_name': f'Test{i+1}',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admins.append(admin_user)
        status = 'Created' if created else 'Using'
        print(f'✓ {status} admin: {admin_user.username} (ID: {admin_user.id})')
    
    return students, teachers, admins

def get_or_create_test_courses():
    """Get or create test courses"""
    courses = []
    try:
        # Try to get existing courses
        courses = list(Course.objects.all()[:5])
        if courses:
            print(f'✓ Using {len(courses)} existing courses')
            return courses
    except:
        pass
    
    # If no courses exist, create dummy ones
    teachers = list(Teacher.objects.all()[:2])
    for i in range(3):
        course = Course.objects.create(
            title=f'Test Course {i+1}',
            description=f'Test course description {i+1}',
            teacher=teachers[i % len(teachers)] if teachers else None,
            category='Technology',
            cost=Decimal('99.99')
        )
        courses.append(course)
        print(f'✓ Created course: {course.title}')
    
    return courses

def get_or_create_plans():
    """Get or create subscription plans"""
    plans = []
    try:
        plans = list(SubscriptionPlan.objects.all()[:3])
        if plans:
            print(f'✓ Using {len(plans)} existing plans')
            return plans
    except:
        pass
    
    # Create dummy plans
    plan_data = [
        {'name': 'Basic', 'duration_days': 30, 'price': Decimal('99.99')},
        {'name': 'Pro', 'duration_days': 90, 'price': Decimal('249.99')},
        {'name': 'Premium', 'duration_days': 365, 'price': Decimal('799.99')},
    ]
    
    for data in plan_data:
        plan = SubscriptionPlan.objects.create(**data)
        plans.append(plan)
        print(f'✓ Created plan: {plan.name}')
    
    return plans

def main():
    """Main function to generate audit logs"""
    print('\n' + '='*60)
    print('AUDIT LOGS DATA GENERATOR')
    print('='*60 + '\n')
    
    print('📋 Setting up test data...\n')
    
    # Get or create test users
    students, teachers, admins = get_or_create_test_users()
    
    print()
    
    # Get or create test courses
    courses = get_or_create_test_courses()
    
    print()
    
    # Get or create subscription plans
    plans = get_or_create_plans()
    
    print('\n' + '-'*60)
    print('🚀 GENERATING AUDIT LOGS...\n')
    print('-'*60 + '\n')
    
    upload_count = 0
    payment_count = 0
    access_count = 0
    
    # Generate upload logs (teachers uploading content)
    print('📤 Generating UPLOAD logs...')
    for _ in range(12):
        teacher = random.choice(teachers) if teachers else None
        if teacher:
            if log_upload(teacher_id=teacher.id):
                upload_count += 1
    print(f'✓ Created {upload_count} upload logs\n')
    
    # Generate payment logs (students making payments)
    print('💳 Generating PAYMENT logs...')
    for _ in range(15):
        student = random.choice(students) if students else None
        plan = random.choice(plans) if plans else None
        if student and plan:
            if log_payment(student.id, plan.id):
                payment_count += 1
    print(f'✓ Created {payment_count} payment logs\n')
    
    # Generate access logs (students accessing courses)
    print('🔓 Generating ACCESS logs...')
    for _ in range(25):
        student = random.choice(students) if students else None
        course = random.choice(courses) if courses else None
        if student and course:
            if log_access(student.id, course_id=course.id):
                access_count += 1
    print(f'✓ Created {access_count} access logs\n')
    
    print('='*60)
    print('✅ AUDIT LOGS GENERATION COMPLETE!')
    print('='*60)
    print(f'''
📊 Summary:
   • Upload Logs:   {upload_count} created
   • Payment Logs:  {payment_count} created
   • Access Logs:   {access_count} created
   • Total:         {upload_count + payment_count + access_count} logs
    
🌐 View the data at: http://127.0.0.1:3000/admin/audit-logs
    ''')
    print('='*60 + '\n')

if __name__ == '__main__':
    main()
