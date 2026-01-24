#!/usr/bin/env python
"""
Quick reference script to display login credentials for testing
"""

print("=" * 70)
print("🎵 HARMONY MUSIC ACADEMY - LOGIN CREDENTIALS 🎵")
print("=" * 70)

print("\n📋 ADMIN USERS:")
print("-" * 70)
print("Super Admin:")
print("  Email:    sarah.anderson@harmonymusic.com")
print("  Password: admin123")
print("  Role:     Super Admin (Full Access)")

print("\nSchool Admin:")
print("  Email:    michael.roberts@harmonymusic.com")
print("  Password: admin123")
print("  Role:     School Admin")

print("\nContent Admin:")
print("  Email:    emily.chen@harmonymusic.com")
print("  Password: admin123")
print("  Role:     Content Admin")

print("\n" + "=" * 70)
print("👨‍🏫 TEACHERS (Sample):")
print("-" * 70)
teachers = [
    ("Dr. James Harrison", "james.harrison@harmonymusic.com", "Piano, Theory, Composition"),
    ("Maria Rodriguez", "maria.rodriguez@harmonymusic.com", "Vocals, Opera, Jazz"),
    ("David Thompson", "david.thompson@harmonymusic.com", "Guitar (All Styles)"),
    ("Lisa Chen", "lisa.chen@harmonymusic.com", "Violin, Chamber Music"),
    ("Robert Davis", "robert.davis@harmonymusic.com", "Drums, Percussion"),
]

for name, email, specialty in teachers:
    print(f"\n{name}")
    print(f"  Email:    {email}")
    print(f"  Password: teacher123")
    print(f"  Teaches:  {specialty}")

print("\n" + "=" * 70)
print("👨‍🎓 STUDENTS (Sample):")
print("-" * 70)
students = [
    ("Emma Thompson", "emma.thompson@email.com", "Piano, Classical"),
    ("Noah Williams", "noah.williams@email.com", "Guitar, Rock"),
    ("Olivia Martinez", "olivia.martinez@email.com", "Vocals, Pop"),
    ("Liam Johnson", "liam.johnson@email.com", "Drums, Jazz"),
    ("Ava Brown", "ava.brown@email.com", "Violin, Classical"),
]

for name, email, interests in students:
    print(f"\n{name}")
    print(f"  Email:     {email}")
    print(f"  Password:  student123")
    print(f"  Interests: {interests}")

print("\n" + "=" * 70)
print("🏫 SCHOOLS:")
print("-" * 70)
print("\nDowntown Campus")
print("  Location: Los Angeles, CA")
print("  Email:    downtown@harmonymusic.com")
print("  Phone:    +1 (555) 200-1000")
print("  Plan:     Premium ($5,999/year)")

print("\nWestside Branch")
print("  Location: Santa Monica, CA")
print("  Email:    westside@harmonymusic.com")
print("  Phone:    +1 (555) 200-2000")
print("  Plan:     Basic ($3,999/year)")

print("\n" + "=" * 70)
print("📊 QUICK STATS:")
print("-" * 70)
print("  • 23 Music Courses (Piano, Guitar, Vocals, Drums, etc.)")
print("  • 73 Active Enrollments")
print("  • 55 Course Ratings (avg 4-5 stars)")
print("  • 30 Student Assignments")
print("  • 7 Quizzes with questions")
print("  • 24 Video Lessons/Chapters")
print("  • 10 Course Categories")

print("\n" + "=" * 70)
print("🚀 TO START TESTING:")
print("-" * 70)
print("  1. Start the server: python manage.py runserver")
print("  2. Login with any credentials above")
print("  3. Test admin dashboard functionality")
print("  4. Check analytics, reports, and user management")
print("\n  To reset database: python manage.py reset_and_seed_music")
print("=" * 70)
