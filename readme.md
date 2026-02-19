# University Management System - Backend

## Seed Credentials
The database has been seeded with the following users:

| **Role** | **Email**               | **Password   | **ID**   |
|----------|-------------------------|--------------|----------|
| Admin    | `admin@university.edu`  | `admin123`   |    -     |
| Faculty  | `rahman@university.edu` | `faculty123` | `FAC001` |
| Student  | `ayesha@university.edu` | `student123` | `STU001` |



### Start Server:
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
