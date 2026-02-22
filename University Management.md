# University Management System — Detailed Role Workflows & Backend Requirements

> **Purpose**: This document serves as a comprehensive reference for building the Django backend. Every workflow, data field, validation rule, and API need described here is derived directly from reading the entire frontend codebase.

---

## Table of Contents

1. [Authentication & Login System](#1-authentication--login-system)
2. [Admin Role — Complete Workflows](#2-admin-role--complete-workflows)
3. [Faculty Role — Complete Workflows](#3-faculty-role--complete-workflows)
4. [Student Role — Complete Workflows](#4-student-role--complete-workflows)
5. [Shared Components](#5-shared-components)
6. [Data Field Reference Tables](#6-data-field-reference-tables)
7. [Grade Scale & GPA Calculation](#7-grade-scale--gpa-calculation)
8. [Backend Validation Rules](#8-backend-validation-rules)

---

## 1. Authentication & Login System

**Source**: `LoginPage.jsx`, `App.jsx`

### 1.1. Login Flow

1. User lands on `LoginPage`.
2. User selects a **role** by clicking one of three buttons: **Admin**, **Faculty**, or **Student** (default is `student`).
3. User enters **Email/Username** (text input, required) and **Password** (password input, required).
4. User clicks **"Sign In"** button.
5. System authenticates and returns a user object with: `role`, `name`, `email`, `id`.
6. Based on `role`, the system mounts the corresponding dashboard component.

### 1.2. Login Data (What Backend Must Return on Login)

```json
{
  "role": "admin | faculty | student",
  "name": "Full Name String",
  "email": "user@university.edu",
  "id": "ADM001 | FAC001 | STU001"
}
```

### 1.3. Forgot Password

- A "Forgot Password?" link exists.
- On click, it should trigger a password reset email workflow.
- **Backend needs**: `POST /api/auth/forgot-password/` endpoint accepting `{ email }`.

### 1.4. Logout

- Each dashboard has a **Logout** button in the header.
- Clicking it clears `currentUser` state (frontend) and should invalidate JWT tokens (backend).

### 1.5. Mock Users (Reference Data for Seeding)

| Role    | Name               | ID     |
|---------|--------------------|--------|
| Admin   | Dr. Harun Ur Rashid| ADM001 |
| Faculty | Prof. Rahman       | FAC001 |
| Student | Ayesha Siddiqua    | STU001 |

---

## 2. Admin Role — Complete Workflows

**Source**: `AdminDashboard.jsx` and all files in `components/admin/`

The Admin has **7 navigation views**: Overview, Manage Students, Manage Faculty, Manage Courses, Assign Courses, Student Enrollment, Academic Records.

---

### 2.1. Admin Overview Dashboard

**Source**: `AdminDashboard.jsx` → `OverviewCards`

**What it displays**:
- **Statistics Cards** (3 cards):
  - Total Students (e.g., "2,847") — **Backend needs**: `GET /api/stats/students/count/`
  - Total Faculty (e.g., "186") — **Backend needs**: `GET /api/stats/faculty/count/`
  - Total Courses (e.g., "342") — **Backend needs**: `GET /api/stats/courses/count/`
- **Quick Action Buttons** (3 buttons):
  - "Add New Student" → should navigate to Manage Students view
  - "Add New Faculty" → should navigate to Manage Faculty view
  - "Create New Course" → should navigate to Manage Courses view

**Backend API needed**: `GET /api/dashboard/admin/stats/` returning `{ total_students, total_faculty, total_courses }`.

---

### 2.2. Manage Students (Full CRUD)

**Source**: `ManageStudents.jsx`

#### 2.2.1. List Students

- Displays a **paginated table** (5 items per page) with columns:
  - Student ID, Name, Email, Major, Year, GPA, Actions
- **Search**: Filters by name, email, or student ID (case-insensitive substring match).
- **Pagination**: Previous/Next buttons + page number buttons. Shows "Showing X to Y of Z students".

**Backend API**: `GET /api/users/students/?search=&page=&page_size=5`
- Must support search across `name`, `email`, `student_id` fields.
- Must return paginated results with total count.

#### 2.2.2. Add Student (Create)

Opens a **modal form** with these fields:

| Field              | Type     | Required | Notes                                      |
|--------------------|----------|----------|--------------------------------------------|
| Student ID         | text     | Yes      | Auto-generated as `STU` + random 3 digits  |
| Full Name          | text     | Yes      |                                            |
| Email              | email    | Yes      |                                            |
| Temporary Password | text     | Yes      | **Only shown when adding** (not editing)   |
| Major              | text     | Yes      | e.g., "Computer Science"                   |
| Year               | select   | Yes      | Options: 1st, 2nd, 3rd, 4th               |
| GPA                | text     | Yes      | e.g., "3.75"                               |

**Backend API**: `POST /api/users/students/`
```json
{
  "student_id": "STU007",
  "name": "Full Name",
  "email": "email@university.edu",
  "password": "tempPass123",
  "major": "Computer Science",
  "year": "3rd",
  "gpa": "3.75"
}
```
**Backend must**: Create a `User` record (role=student) AND a `Student` profile record. The `password` field creates the user's login credentials.

#### 2.2.3. Edit Student (Update)

- Opens the **same modal** but pre-filled with existing data.
- The **Temporary Password field is hidden** during editing.
- All other fields are editable.
- Button text changes to "Update Student".

**Backend API**: `PUT /api/users/students/{student_id}/`

#### 2.2.4. Delete Student

- Clicking the delete (trash) icon triggers a **browser confirm dialog**: "Are you sure you want to delete this student?"
- On confirm, the student record is removed.

**Backend API**: `DELETE /api/users/students/{student_id}/`
**Backend must**: Delete both the `Student` profile and the associated `User` record (or deactivate).

---

### 2.3. Manage Faculty (Full CRUD)

**Source**: `ManageFaculty.jsx`

#### 2.3.1. List Faculty

- **Paginated table** (5 items per page) with columns:
  - Faculty ID, Name, Email, Department, Specialization, Join Date, Actions
- **Search**: Filters by name, email, or department (case-insensitive).

**Backend API**: `GET /api/users/faculty/?search=&page=&page_size=5`

#### 2.3.2. Add Faculty (Create)

Modal form fields:

| Field              | Type     | Required | Notes                                         |
|--------------------|----------|----------|-----------------------------------------------|
| Faculty ID         | text     | Yes      | Auto-generated as `FAC` + random 3 digits     |
| Full Name          | text     | Yes      |                                               |
| Email              | email    | Yes      |                                               |
| Temporary Password | text     | Yes      | **Only shown when adding** (not editing)      |
| Department         | text     | Yes      | e.g., "Computer Science"                      |
| Specialization     | text     | Yes      | e.g., "Database Systems"                      |
| Join Date          | date     | Yes      | Date picker input                             |

**Backend API**: `POST /api/users/faculty/`
```json
{
  "faculty_id": "FAC006",
  "name": "Full Name",
  "email": "email@university.edu",
  "password": "tempPass123",
  "department": "Computer Science",
  "specialization": "Database Systems",
  "join_date": "2025-01-15"
}
```
**Backend must**: Create a `User` record (role=faculty) AND a `Faculty` profile record.

#### 2.3.3. Edit Faculty (Update)

- Same modal, pre-filled, password field hidden.
- Button: "Update Faculty".

**Backend API**: `PUT /api/users/faculty/{faculty_id}/`

#### 2.3.4. Delete Faculty

- Confirm dialog: "Are you sure you want to delete this faculty member?"

**Backend API**: `DELETE /api/users/faculty/{faculty_id}/`

---

### 2.4. Manage Courses (Full CRUD with Scheduling)

**Source**: `ManageCourses.jsx`

This is a **combined view** that manages both course catalog data AND class schedule/location data in a single form.

#### 2.4.1. List Courses

- **Paginated table** (5 items per page) with columns:
  - Course Code, Course Name, Department, Schedule (days + time), Location (building + room), Actions
- **Search**: Filters by course name, code, or department.

**Backend API**: `GET /api/academic/courses/?search=&page=&page_size=5`
- Response must include schedule and location data joined.

#### 2.4.2. Add Course (Create)

Modal form fields (**two sections**: Course Info + Schedule & Location):

**Course Information Section:**

| Field       | Type    | Required | Notes                        |
|-------------|---------|----------|------------------------------|
| Course Code | text    | Yes      | e.g., "CS301"                |
| Credits     | number  | Yes      | Min: 1, Max: 6               |
| Course Name | text    | Yes      |                              |
| Department  | text    | Yes      | e.g., "Computer Science"     |
| Semester    | text    | Yes      | e.g., "Fall 2025"            |

**Class Schedule & Location Section:**

| Field         | Type            | Required | Notes                                      |
|---------------|-----------------|----------|--------------------------------------------|
| Class Days    | multi-toggle    | No       | Options: Mon, Tue, Wed, Thu, Fri, Sat, Sun |
| Start Time    | time            | No       | Time picker                                |
| End Time      | time            | No       | Time picker                                |
| Room Number   | text            | No       | e.g., "301"                                |
| Building Name | text            | No       | e.g., "Academic Block A"                   |

**Day selection UI**: Toggle buttons (pill-shaped), multiple can be selected. Selected days are stored as an **array** (e.g., `["Mon", "Wed"]`).

**Backend API**: `POST /api/academic/courses/`
```json
{
  "code": "CS301",
  "name": "Database Systems",
  "department": "Computer Science",
  "credits": 3,
  "semester": "Fall 2025",
  "days": ["Mon", "Wed"],
  "start_time": "10:00",
  "end_time": "11:30",
  "room": "301",
  "building": "Academic Block A"
}
```

**Backend consideration**: This single form creates/edits BOTH a `Course` record AND a `ClassSchedule` record. The backend can either:
- Accept this combined payload and handle the creation of both internally, OR
- The frontend can be updated to make two separate API calls.

#### 2.4.3. Edit Course (Update)

- Same modal, pre-filled with all data including schedule/location.
- Day toggles reflect current selected days.

**Backend API**: `PUT /api/academic/courses/{course_id}/`

#### 2.4.4. Delete Course

- Confirm dialog: "Are you sure you want to delete this course?"

**Backend API**: `DELETE /api/academic/courses/{course_id}/`

---

### 2.5. Assign Courses to Faculty

**Source**: `AssignCourses.jsx`

#### 2.5.1. Assignment Form

1. Admin selects a **Faculty Member** from a dropdown showing `Name (ID)`.
2. Admin selects a **Course** from a dropdown showing `Code - Name`.
3. Clicks **"Assign Course"** button.
4. On success, a green **success alert** appears for 3 seconds: "Course assigned successfully!"
5. The new assignment appears in the table below.

**Backend API**: `POST /api/academic/assignments/`
```json
{
  "faculty_id": "FAC001",
  "course_id": "CRS001"
}
```

#### 2.5.2. Current Assignments Table

Displays existing assignments with columns:
- Faculty ID, Faculty Name, Course Code, Course Name

**Backend API**: `GET /api/academic/assignments/`
- Returns list of all faculty-course mappings.

**Backend needs for dropdowns**:
- `GET /api/users/faculty/` → returns `[{ id, name }]` for dropdown population
- `GET /api/academic/courses/` → returns `[{ id, code, name }]` for dropdown population

---

### 2.6. Student Enrollment (Admin-Side)

**Source**: `StudentEnrollment.jsx`

#### 2.6.1. Enrollment Form

1. Admin selects a **Student** from dropdown showing `Name (ID)`.
2. Admin selects a **Course** from dropdown showing `Name (Code)`.
3. Clicks **"Enroll Student"** button.
4. **Duplicate check**: If the student is already enrolled in the selected course, an alert shows: "Student is already enrolled in this course."
5. On success, the enrollment record appears in the table.

**Backend API**: `POST /api/academic/enrollments/`
```json
{
  "student_id": "STU001",
  "course_code": "CS301"
}
```
**Backend must validate**: No duplicate enrollment for the same student + course combination.

#### 2.6.2. Enrollment List

- **Search**: Filters by student name, student ID, or course code.
- **Table columns**: Student Name, Student ID, Course Code, Course Name, Semester, Instructor, Action (remove button).

**Backend API**: `GET /api/academic/enrollments/?search=`

#### 2.6.3. Remove Enrollment

- Clicking trash icon triggers confirm: "Are you sure you want to remove this enrollment?"

**Backend API**: `DELETE /api/academic/enrollments/{enrollment_id}/`

**Enrollment record fields** (what backend must store and return):

| Field        | Notes                       |
|--------------|-----------------------------|
| id           | Auto-generated unique ID    |
| studentName  | Resolved from Student       |
| studentId    | Foreign key to Student      |
| courseCode   | Foreign key to Course       |
| courseName   | Resolved from Course        |
| semester     | Resolved from Course/Schedule |
| instructor   | Resolved from Assignment    |

---

### 2.7. Academic Records (Read-Only View)

**Source**: `ViewRecords.jsx`

#### 2.7.1. Features

- **Read-only** — admin cannot edit grades from this view.
- **Search**: Filters by student name, student ID, or course code.
- **Semester Filter**: Dropdown populated with unique semesters from the data (e.g., "Fall 2025", "Spring 2025").
- **Paginated** (8 items per page).

#### 2.7.2. Table Columns

- Student ID, Student Name, Course Code, Course Name, Grade (with color badge), Credits, Semester

#### 2.7.3. Grade Badges (Color Coding)

| Grade Starts With | Badge Style  | Color  |
|-------------------|-------------|--------|
| A                 | badge-success | Green  |
| B                 | badge-primary | Blue   |
| C                 | badge-warning | Yellow |
| D or F            | badge-danger  | Red    |

**Backend API**: `GET /api/academic/records/?search=&semester=&page=&page_size=8`
- Must support filtering by student name/ID/course code AND by semester.
- Must return all grade records across all students.

---

## 3. Faculty Role — Complete Workflows

**Source**: `FacultyDashboard.jsx` and all files in `components/faculty/`

The Faculty has **5 navigation views**: Overview, Assigned Courses, View Students, Submit Grades, Update Grades.

---

### 3.1. Faculty Overview Dashboard

**Source**: `FacultyDashboard.jsx` → `OverviewCards`

**Statistics Cards** (2 cards):
- Assigned Courses count (e.g., "4") — **Backend**: courses assigned to this faculty
- Total Students count (e.g., "187") — **Backend**: total students enrolled in this faculty's courses

**Class Schedule Widget**: Shows today's/tomorrow's classes for this faculty (see Section 5).

**Backend API**: `GET /api/dashboard/faculty/stats/` (filtered by authenticated faculty user)
- Returns `{ assigned_courses_count, total_students_count }`
- Also: `GET /api/academic/schedules/?faculty=current` for class schedule widget data.

---

### 3.2. View Assigned Courses

**Source**: `ViewAssignedCourses.jsx`

#### 3.2.1. Course Cards Grid

Displays courses as a **responsive grid of cards** (not a table). Each card shows:

| Field            | Notes                                   |
|------------------|-----------------------------------------|
| Course Code      | e.g., "CS301"                           |
| Course Name      | e.g., "Database Systems"                |
| Status Badge     | "Active" (green badge)                  |
| Semester         | e.g., "Fall 2025"                       |
| Enrolled Students| Count, e.g., "48"                       |
| Credits          | e.g., "3"                               |
| "View Details"   | Button to open detail modal             |

**Backend API**: `GET /api/academic/courses/?faculty=current`
- Must return only courses assigned to the authenticated faculty.
- Each course must include: `code`, `name`, `semester`, `students_count`, `credits`, `time`, `room`, `description`.

#### 3.2.2. Course Details Modal

Opened by clicking "View Details". Displays:

| Field       | Icon      | Data Example                                              |
|-------------|-----------|-----------------------------------------------------------|
| Semester    | Calendar  | "Fall 2025"                                               |
| Credits     | Book      | "3 Credits"                                               |
| Schedule    | Clock     | "Mon, Wed 10:00 AM"                                       |
| Location    | MapPin    | "Bldg A - 302"                                            |
| Description | —         | Full text description of the course                       |

---

### 3.3. View Students (Enrolled in Faculty's Courses)

**Source**: `ViewStudents.jsx`

#### 3.3.1. Filters

- **Search**: By student name, email, or student ID.
- **Course Filter**: Dropdown with all courses (derived from unique course values in the student list).

#### 3.3.2. Students Table

Columns: Student ID, Name, Email, Course (format: "CS301 - Database Systems"), Enrollment Date

**Backend API**: `GET /api/academic/enrollments/?faculty=current&search=&course=`
- Must return only students enrolled in courses taught by the authenticated faculty.
- Each record includes: `student_id`, `name`, `email`, `course` (code + name), `enrollment_date`.

---

### 3.4. Submit Grades (New Grade Entry)

**Source**: `SubmitGrades.jsx`

#### 3.4.1. Workflow

1. Faculty selects a **Course** from dropdown showing `Code - Name`.
2. System populates the list of enrolled students for that course.
3. If **no students** are enrolled, a message shows: "No students enrolled in this course yet."
4. For each student shown, faculty selects a **Grade** from dropdown.
5. Faculty clicks **"Submit All Grades"** button.
6. Success alert: "Grades submitted successfully!" (shown for 2 seconds).
7. After success, the form resets (course selection cleared, grade list cleared).

#### 3.4.2. Grade Entry UI

For each student, displayed as a row:
- Left side: Student Name + Student ID
- Right side: Grade dropdown

#### 3.4.3. Available Grade Options

`A`, `A-`, `B+`, `B`, `B-`, `C+`, `C`, `C-`, `D`, `F`

**Backend API**: `POST /api/academic/grades/bulk/`
```json
{
  "course_code": "CS301",
  "grades": [
    { "student_id": "STU001", "grade": "A" },
    { "student_id": "STU002", "grade": "B+" }
  ]
}
```

**Backend must**:
- Look up enrollments for the given course + students.
- Create `Grade` records linked to each enrollment.
- Calculate GPA points based on the grade scale.
- Restrict: only the assigned faculty can grade their own courses.

**Prerequisite API for dropdown**: `GET /api/academic/enrollments/?course=CS301` → returns students enrolled in that course.

---

### 3.5. Update Grades (Modify Existing Grades)

**Source**: `UpdateGrades.jsx`

#### 3.5.1. Existing Grades Table

Displays ALL previously submitted grades by this faculty:
- Columns: Student ID, Student Name, Course (Code - Name), Current Grade (color badge), Action (Edit button)
- **Search**: By student name, student ID, or course code.

**Backend API**: `GET /api/academic/grades/?faculty=current&search=`

#### 3.5.2. Edit Grade Modal

When faculty clicks "Edit" on a row:

1. A modal opens showing:
   - **Student** (read-only): "Name (ID)"
   - **Course** (read-only): "Code - Name"
   - **New Grade** dropdown (same A through F options as Submit Grades)
2. Faculty selects new grade and clicks **"Update Grade"**.
3. Success alert: "Grade updated successfully!" (3 seconds).

**Backend API**: `PUT /api/academic/grades/{grade_id}/`
```json
{
  "grade": "A-"
}
```

**Backend must**:
- Validate that only the faculty who originally graded can update.
- Recalculate GPA points on update.
- Optionally log the grade change history.

---

## 4. Student Role — Complete Workflows

**Source**: `StudentDashboard.jsx` and all files in `components/student/`

The Student has **4 navigation views**: Overview, Course Enrollment, View Grades, Academic Records.

---

### 4.1. Student Overview Dashboard

**Source**: `StudentDashboard.jsx` → `OverviewCards`

**Statistics Cards** (2 cards):
- Enrolled Courses count (e.g., "5")
- Current GPA (e.g., "3.72")

**Class Schedule Widget**: Shows today's/tomorrow's classes for this student (see Section 5).

**Current Semester Courses List**: Shows all enrolled courses with an "In Progress" badge. Example courses shown:
- CS301 - Database Systems
- MATH201 - Linear Algebra
- PHY101 - Physics I
- ENG202 - Technical Writing
- CS302 - Algorithms

**Backend API**: `GET /api/dashboard/student/stats/`
- Returns `{ enrolled_courses_count, current_gpa }`
- Also: `GET /api/academic/enrollments/?student=current&semester=active` for enrolled courses list.
- Also: `GET /api/academic/schedules/?student=current` for class schedule widget.

---

### 4.2. Course Enrollment (View Currently Enrolled)

**Source**: `ViewEnrollment.jsx`

#### 4.2.1. Enrollment Table

Displays the student's **currently enrolled courses** in a table:

| Column      | Example Data                  |
|-------------|-------------------------------|
| Course Code | CS301                         |
| Course Name | Database Systems              |
| Instructor  | Prof. Rahman                  |
| Credits     | 3                             |
| Schedule    | Mon, Wed 10:00-11:30          |
| Room        | 301 - Block A                 |
| Status      | "Active" (green badge)        |

**Backend API**: `GET /api/academic/enrollments/?student=current`
- Must return resolved data: course + instructor + schedule + room info.

#### 4.2.2. Enrollment Summary Box

Shows below the table:
- **Total Courses**: count of enrolled courses (e.g., 5)
- **Total Credits**: sum of all enrolled course credits (e.g., 17)

These are **calculated on the frontend** from the enrollment data.

---

### 4.3. View Grades

**Source**: `ViewGrades.jsx`

#### 4.3.1. GPA Card (Prominent Header)

Displays:
- **Current GPA**: Calculated as weighted average → `Σ(grade_points × credits) / Σ(credits)`
- **Semester Label**: e.g., "Fall 2025 Semester"
- **Total Credits**: Sum of all credits

#### 4.3.2. Grades Table

| Column       | Notes                              |
|--------------|-------------------------------------|
| Course Code  | e.g., "CS301"                       |
| Course Name  | e.g., "Database Systems"            |
| Credits      | e.g., 3                             |
| Grade        | Color-coded badge (see Section 7)   |
| Grade Points | Numeric, e.g., 4.0 for "A"         |
| Semester     | e.g., "Fall 2025"                   |

#### 4.3.3. Summary Stats Cards (Bottom)

Three gradient cards:
- **Total Courses**: count
- **Average Grade**: calculated GPA
- **Credits Earned**: sum of credits

#### 4.3.4. Export Transcript

- An **"Export Transcript"** button (with download icon) exists in the header.
- Currently shows a mock alert. Backend should provide a PDF generation endpoint.

**Backend API**: `GET /api/academic/grades/?student=current`
**Transcript API**: `GET /api/academic/transcript/?student=current&format=pdf`

---

### 4.4. Academic History (Semester-by-Semester Records)

**Source**: `AcademicHistory.jsx`

#### 4.4.1. Overall Academic Summary (Top Section)

Four stats cards showing cumulative data:

| Stat              | Example | Color   |
|-------------------|---------|---------|
| Cumulative GPA    | 3.72    | Purple  |
| Total Credits     | 51      | Blue    |
| Semesters         | 3       | Green   |
| Courses Completed | 13      | Orange  |

**Backend API**: `GET /api/academic/history/summary/?student=current`

#### 4.4.2. Semester-by-Semester Breakdown

For **each semester**, displayed as a separate card/table:

**Header**: Semester name (e.g., "Fall 2025") + Semester GPA (e.g., "3.72")

**Table per semester**:
- Columns: Course Code, Course Name, Credits, Grade (color badge)
- Footer: "Total Credits: X" (sum of credits for that semester)

**Data structure the backend must return**:
```json
[
  {
    "semester": "Fall 2025",
    "gpa": 3.72,
    "courses": [
      { "code": "CS301", "name": "Database Systems", "grade": "A", "credits": 3 },
      { "code": "MATH201", "name": "Linear Algebra", "grade": "A-", "credits": 4 }
    ]
  },
  {
    "semester": "Spring 2025",
    "gpa": 3.77,
    "courses": [...]
  }
]
```

**Backend API**: `GET /api/academic/history/?student=current`
- Must return data grouped by semester, ordered by most recent first.
- Each semester includes its calculated GPA and list of courses with grades.

---

## 5. Shared Components

### 5.1. Class Schedule Widget

**Source**: `ClassScheduleWidget.jsx`

A shared widget used by **both Faculty and Student** overview dashboards.

#### 5.1.1. Features

- **Toggle between "Today" and "Tomorrow"** via tab buttons.
- Filters classes based on the current day of the week.
- If no classes on the selected day, shows: "No classes scheduled for today/tomorrow."

#### 5.1.2. Each Class Entry Shows

| Field       | Notes                                                     |
|-------------|-----------------------------------------------------------|
| Time Block  | Start time, "to", End time (left column)                  |
| Course Name | Bold header                                                |
| Course Code | With type label (e.g., "CS301 • Lecture")                  |
| Status      | Badge: "Scheduled" (green) or "Cancelled" (red)           |
| Location    | MapPin icon + "Room (Building)"                           |
| Instructor  | **Only shown for student role** (Calendar icon + name)     |

#### 5.1.3. Data Shape Required

```json
{
  "courseCode": "CS301",
  "courseName": "Database Systems",
  "startTime": "10:00",
  "endTime": "11:30",
  "days": ["Mon", "Wed"],
  "room": "301",
  "building": "Academic Block A",
  "type": "Lecture",
  "status": "Scheduled",
  "instructor": "Prof. Rahman"  // only for student view
}
```

**Backend API**: `GET /api/academic/schedules/today/?role=faculty|student`

---

## 6. Data Field Reference Tables

### 6.1. Student Entity

| Field           | Type    | Constraints                     | Source Component    |
|-----------------|---------|---------------------------------|---------------------|
| student_id      | string  | Unique, format: "STU" + digits  | ManageStudents      |
| name            | string  | Required                        | ManageStudents      |
| email           | email   | Required, unique                | ManageStudents      |
| password        | string  | Required on create only         | ManageStudents      |
| major           | string  | Required (department name)      | ManageStudents      |
| year            | enum    | "1st", "2nd", "3rd", "4th"      | ManageStudents      |
| gpa             | decimal | Required on create, recalculated| ManageStudents      |

### 6.2. Faculty Entity

| Field           | Type    | Constraints                     | Source Component    |
|-----------------|---------|---------------------------------|---------------------|
| faculty_id      | string  | Unique, format: "FAC" + digits  | ManageFaculty       |
| name            | string  | Required                        | ManageFaculty       |
| email           | email   | Required, unique                | ManageFaculty       |
| password        | string  | Required on create only         | ManageFaculty       |
| department      | string  | Required                        | ManageFaculty       |
| specialization  | string  | Required                        | ManageFaculty       |
| join_date       | date    | Required, format: YYYY-MM-DD    | ManageFaculty       |

### 6.3. Course Entity (Combined with Schedule)

| Field      | Type        | Constraints                     | Source Component   |
|------------|-------------|---------------------------------|--------------------|
| code       | string      | Required, unique (e.g., "CS301")| ManageCourses      |
| name       | string      | Required                        | ManageCourses      |
| department | string      | Required                        | ManageCourses      |
| credits    | integer     | Required, range: 1-6            | ManageCourses      |
| semester   | string      | Required (e.g., "Fall 2025")    | ManageCourses      |
| days       | array/JSON  | Array of day strings            | ManageCourses      |
| start_time | time        | Format: HH:MM                  | ManageCourses      |
| end_time   | time        | Format: HH:MM                  | ManageCourses      |
| room       | string      | Room number                     | ManageCourses      |
| building   | string      | Building name                   | ManageCourses      |

### 6.4. Enrollment Entity

| Field        | Type     | Constraints                           | Source Component     |
|--------------|----------|---------------------------------------|----------------------|
| id           | integer  | Auto-generated                        | StudentEnrollment    |
| student_id   | FK       | References Student                    | StudentEnrollment    |
| course_code  | FK       | References Course                     | StudentEnrollment    |
| semester     | string   | Resolved from course/schedule         | StudentEnrollment    |
| instructor   | string   | Resolved from assignment              | StudentEnrollment    |
| status       | enum     | "Active", "Enrolled", "Dropped", etc. | ViewEnrollment       |

### 6.5. Grade Entity

| Field        | Type    | Constraints                     | Source Component |
|--------------|---------|---------------------------------|------------------|
| student_id   | FK      | References Student              | SubmitGrades     |
| course_code  | FK      | References Course               | SubmitGrades     |
| grade        | enum    | See Grade Scale below           | SubmitGrades     |
| grade_points | decimal | Calculated from grade           | ViewGrades       |

### 6.6. Faculty-Course Assignment Entity

| Field        | Type   | Constraints          | Source Component |
|--------------|--------|----------------------|------------------|
| faculty_id   | FK     | References Faculty   | AssignCourses    |
| course_id    | FK     | References Course    | AssignCourses    |

---

## 7. Grade Scale & GPA Calculation

### 7.1. Grade-to-Points Mapping

| Letter Grade | Grade Points |
|:-------------|:-------------|
| A            | 4.0          |
| A-           | 3.7          |
| B+           | 3.3          |
| B            | 3.0          |
| B-           | 2.7          |
| C+           | 2.3          |
| C            | 2.0          |
| C-           | 1.7          |
| D            | 1.0          |
| F            | 0.0          |

### 7.2. GPA Calculation Formula

```
GPA = Σ(grade_points[i] × credits[i]) / Σ(credits[i])
```

**Example** (from ViewGrades):
- CS301: A (4.0) × 3 credits = 12.0
- MATH201: A- (3.7) × 4 credits = 14.8
- PHY101: B+ (3.3) × 4 credits = 13.2
- ENG202: A (4.0) × 3 credits = 12.0
- CS302: A- (3.7) × 3 credits = 11.1
- **Total**: 63.1 / 17 = **3.71**

**Backend must**: Calculate and store GPA whenever grades are submitted or updated. The `Student.current_gpa` field should be a cached value updated on every grade change.

### 7.3. Grade Badge Color Coding

Used consistently across admin ViewRecords, faculty UpdateGrades, and student ViewGrades/AcademicHistory:

| Grade Prefix | CSS Class     | Visual Color |
|:-------------|:-------------|:-------------|
| A            | grade-A / badge-success | Green |
| B            | grade-B / badge-primary | Blue  |
| C            | grade-C / badge-warning | Yellow|
| D / F        | grade-D / badge-danger  | Red   |

---

## 8. Backend Validation Rules

### 8.1. Authentication

- Email must be unique across all users.
- Role must be one of: `admin`, `faculty`, `student`.
- JWT tokens: access + refresh pair.
- Role-based permissions on every endpoint.

### 8.2. Student Management

- `student_id` must be unique.
- `email` must be unique.
- `year` must be one of: `1st`, `2nd`, `3rd`, `4th`.
- `gpa` should be a valid decimal (0.00 to 4.00).

### 8.3. Faculty Management

- `faculty_id` must be unique.
- `email` must be unique.
- `join_date` must be a valid date.

### 8.4. Course Management

- `code` must be unique (e.g., "CS301").
- `credits` must be between 1 and 6.
- `days` must be a JSON array of valid day strings.
- Time conflict check: when creating/editing a schedule, verify that the selected classroom is not already booked for the same day/time.
- Faculty conflict check: verify faculty is not scheduled for overlapping time slots.

### 8.5. Enrollment

- **Duplicate check**: A student cannot be enrolled in the same course twice.
- Enrollment creates a link between Student and ClassSchedule (course + semester).

### 8.6. Grading

- Only the **assigned faculty** can submit/update grades for their course.
- Grade must be one of the 10 valid values (A through F).
- GPA points are auto-calculated by backend based on the grade scale.
- After any grade change, the student's `current_gpa` must be recalculated.
- A grade can only be submitted for an existing enrollment.

### 8.7. Permission Matrix

| Endpoint Category    | Admin | Faculty | Student |
|---------------------|:-----:|:-------:|:-------:|
| Manage Students     | ✅    | ❌      | ❌      |
| Manage Faculty      | ✅    | ❌      | ❌      |
| Manage Courses      | ✅    | ❌      | ❌      |
| Assign Courses      | ✅    | ❌      | ❌      |
| Student Enrollment  | ✅    | ❌      | ❌      |
| View All Records    | ✅    | ❌      | ❌      |
| View Assigned Courses| ❌   | ✅      | ❌      |
| View Enrolled Students| ❌  | ✅      | ❌      |
| Submit Grades       | ❌    | ✅      | ❌      |
| Update Grades       | ❌    | ✅      | ❌      |
| View Own Enrollment | ❌    | ❌      | ✅      |
| View Own Grades     | ❌    | ❌      | ✅      |
| View Own History    | ❌    | ❌      | ✅      |
| Dashboard Stats     | ✅    | ✅      | ✅      |
| Login/Auth          | ✅    | ✅      | ✅      |

---

> **End of Document** — This file covers every workflow, data field, form, validation, and API requirement found in the frontend codebase. Use this as the definitive reference for backend implementation.

