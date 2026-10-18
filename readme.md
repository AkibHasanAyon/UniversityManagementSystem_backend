# 🎓 University Management System — Backend REST API

![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.x-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-Collection%20Included-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

A robust Django REST Framework backend powering a comprehensive University Management System. Supports dedicated role-based portals for **Administrators**, **Faculty Members**, and **Students** with course registrations, grade submissions, GPA calculations, and timetable management.

---

## 👥 Role Matrix & Workflows

### 1. 🛡️ Administrator Role
* **User Management**: Provision and manage student and faculty accounts.
* **Curriculum & Academic Structure**: Create departments, configure courses, set prerequisites, and manage semester terms.
* **Course Assignment**: Assign faculty members to courses and class schedules.
* **Enrollment Management**: Review and authorize student course enrollments.

### 2. 👨‍🏫 Faculty Role
* **Assigned Courses**: View assigned courses, student rosters, and schedules.
* **Grading System**: Submit and modify numerical/letter grades for enrolled students.
* **Student Tracking**: View student academic standing and attendance profiles.

### 3. 🎓 Student Role
* **Course Enrollment**: Browse offered courses and submit enrollment requests according to prerequisites.
* **Academic History & Grades**: View published letter grades, credit completions, semester GPAs, and cumulative CGPA.
* **Schedule**: Access weekly class schedule widgets and timings.

---

## 🔑 Pre-Seeded Demonstration Accounts

The database seed script (`seed_data.py`) provides pre-configured role accounts:

| Role | Email | Password | User ID |
|---|---|---|---|
| **Admin** | `admin@university.edu` | `admin123` | `ADM001` |
| **Faculty** | `rahman@university.edu` | `faculty123` | `FAC001` |
| **Student** | `ayesha@university.edu` | `student123` | `STU001` |

---

## 📁 Project Architecture

```text
UniversityManagementSystem_backend/
├── academic/                          # Academic domain app (courses, grades, schedules)
│   ├── admin.py
│   ├── models.py                      # Course, Department, Enrollment, Grade models
│   ├── serializers.py                 # DRF Serializers with GPA logic
│   ├── urls.py
│   └── views.py                       # Academic ViewSets & permission filters
├── config/                            # Core project settings and URL router
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                             # Authentication and user accounts app
│   ├── models.py                      # Custom User model (Role: Admin/Faculty/Student)
│   ├── permissions.py                 # RBAC permission classes
│   ├── serializers.py
│   └── views.py                       # Login, Logout, and Profile endpoints
├── seed_data.py                       # Automated database population script
├── schema.yaml                        # Complete OpenAPI / Swagger 3.0 API schema
├── University_Management_System.postman_collection.json # Ready-to-import Postman suite
├── requirements.txt                   # Backend Python dependencies
├── manage.py                          # Django management CLI
└── University Management.md           # Full domain specifications document
```

---

## 🚀 Local Setup & Installation

### 1. Create Virtual Environment
```bash
cd UniversityManagementSystem_backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Records
```bash
python manage.py migrate
python seed_data.py
```

### 4. Run Development Server
```bash
python manage.py runserver
```
The REST API will be accessible at `http://127.0.0.1:8000/`.

---

## 🧪 Verification & Testing

Verify system security, standard response structures, and token revocation:

```bash
# Verify standardized API response formats:
python test_standard_responses.py

# Verify session logout and JWT revocation:
python verify_logout.py
```

---

## 🌐 Deployment (PythonAnywhere Guide)

```bash
cd UniversityManagementSystem_backend
source venv/bin/activate
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
# Reload the Web App from the PythonAnywhere dashboard tab
```

