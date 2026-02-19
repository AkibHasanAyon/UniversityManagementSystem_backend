# University Management System - Backend

## Seed Credentials
The database has been seeded with the following users:

| **Role** | **Email**               | **Password   | **ID**   |
|----------|-------------------------|--------------|----------|
| Admin    | `admin@university.edu`  | `admin123`   |    -     |
| Faculty  | `rahman@university.edu` | `faculty123` | `FAC001` |
| Student  | `ayesha@university.edu` | `student123` | `STU001` |



### Start Server Locally:
```bash
source .venv/bin/activate
python manage.py runserver
```

### Run Tests:
```bash
python test_all_endpoints.py
```

### Reset Database
```bash
rm db.sqlite3
python manage.py migrate
python seed_data.py
```

### Update and deploy on PythonAnywhere
```bash
cd UniversityManagementSystem_backend
source venv/bin/activate
git pull origin main
python manage.py migrate
python manage.py collectstatic

click reload from https://www.pythonanywhere.com/user/vondobaba/webapps/#tab_id_vondobaba_pythonanywhere_com
```