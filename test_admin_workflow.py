import os
import django
from django.db.utils import IntegrityError
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from university.models import Classroom, Semester

def test_admin_workflow():
    print("--- Testing Admin setup Validation ---")

    # 1. Classroom Uniqueness
    print("\n1. Testing Classroom Uniqueness...")
    c1 = Classroom(room_number="101", building="Science Block", capacity=50)
    c1.save()
    print("Created Classroom 101 in Science Block.")

    try:
        c2 = Classroom(room_number="101", building="Science Block", capacity=30)
        c2.save()
        print("FAILED: Duplicate classroom created!")
    except IntegrityError:
        print("SUCCESS: Duplicate classroom prevented.")
    except Exception as e:
        print(f"ERROR: {e}")

    # Clean up
    c1.delete()

    # 2. Semester Invariants
    print("\n2. Testing Semester Invariants...")
    s1 = Semester(name="Spring 2024", start_date=date(2024, 1, 1), end_date=date(2024, 6, 30), is_active=True)
    s1.save()
    print(f"Created Active Semester: {s1.name} (Active: {s1.is_active})")

    s2 = Semester(name="Fall 2024", start_date=date(2024, 7, 1), end_date=date(2024, 12, 31), is_active=True)
    s2.save()
    print(f"Created New Active Semester: {s2.name}")

    # Refresh s1
    s1.refresh_from_db()
    print(f"Old Semester {s1.name} Active Status: {s1.is_active}")

    if not s1.is_active and s2.is_active:
        print("SUCCESS: Old semester deactivated.")
    else:
        print("FAILED: Old semester still active.")

    # Clean up
    s1.delete()
    s2.delete()

if __name__ == "__main__":
    test_admin_workflow()
