import sqlite3
from datetime import date
from faker import Faker
import random

# Register date adapters for SQLite
def adapt_date_iso(val):
    return val.isoformat()

def convert_date(val):
    return date.fromisoformat(val.decode())

sqlite3.register_adapter(date, adapt_date_iso)
sqlite3.register_converter("date", convert_date)

# Connect to SQLite database (creates if doesn't exist)
conn = sqlite3.connect('employee_database.db', detect_types=sqlite3.PARSE_DECLTYPES)
cursor = conn.cursor()

# Create departments table
cursor.execute('''
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
''')

# Create employees table
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hire_date DATE,
    department_id INTEGER,
    manager_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (manager_id) REFERENCES employees (id)
)
''')

# Create projects table
cursor.execute('''
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    start_date DATE,
    end_date DATE
)
''')

# Create employee_projects table (many-to-many)
cursor.execute('''
CREATE TABLE IF NOT EXISTS employee_projects (
    employee_id INTEGER,
    project_id INTEGER,
    role TEXT,
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees (id),
    FOREIGN KEY (project_id) REFERENCES projects (id)
)
''')

# Create skills table
cursor.execute('''
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
''')

# Create employee_skills table (many-to-many)
cursor.execute('''
CREATE TABLE IF NOT EXISTS employee_skills (
    employee_id INTEGER,
    skill_id INTEGER,
    proficiency_level TEXT CHECK(proficiency_level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')),
    PRIMARY KEY (employee_id, skill_id),
    FOREIGN KEY (employee_id) REFERENCES employees (id),
    FOREIGN KEY (skill_id) REFERENCES skills (id)
)
''')

# Insert sample departments
departments = [
    ('Human Resources',),
    ('Engineering',),
    ('Sales',),
    ('Marketing',)
]

cursor.executemany('INSERT OR IGNORE INTO departments (name) VALUES (?)', departments)

# Insert sample employees
employees = [
    ('John', 'Doe', 'john.doe@company.com', date(2020, 1, 15), 2, None),  # Engineering, no manager
    ('Jane', 'Smith', 'jane.smith@company.com', date(2020, 3, 20), 2, 1),  # Engineering, manager John
    ('Bob', 'Johnson', 'bob.johnson@company.com', date(2019, 5, 10), 1, None),  # HR, no manager
    ('Alice', 'Williams', 'alice.williams@company.com', date(2021, 7, 5), 3, None),  # Sales, no manager
    ('Charlie', 'Brown', 'charlie.brown@company.com', date(2022, 2, 14), 2, 1),  # Engineering, manager John
    ('Diana', 'Davis', 'diana.davis@company.com', date(2021, 9, 30), 4, None),  # Marketing, no manager
    ('Eve', 'Miller', 'eve.miller@company.com', date(2023, 4, 22), 3, 4),  # Sales, manager Alice
]

cursor.executemany('''
INSERT OR IGNORE INTO employees (first_name, last_name, email, hire_date, department_id, manager_id)
VALUES (?, ?, ?, ?, ?, ?)
''', employees)

# Generate and insert 1000 additional employees
fake = Faker()
fake.unique.clear()  # Reset unique generator

# Get current max employee id
cursor.execute('SELECT MAX(id) FROM employees')
max_id = cursor.fetchone()[0] or 0

additional_employees = []
for _ in range(1000):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    hire_date = fake.date_between(start_date='-5y', end_date='today')
    department_id = fake.random_int(min=1, max=4)
    manager_id = None if fake.boolean(chance_of_getting_true=50) else fake.random_int(min=1, max=max_id)
    additional_employees.append((first_name, last_name, email, hire_date, department_id, manager_id))

cursor.executemany('''
INSERT INTO employees (first_name, last_name, email, hire_date, department_id, manager_id)
VALUES (?, ?, ?, ?, ?, ?)
''', additional_employees)

# Insert sample projects
projects = [
    ('Website Redesign', date(2023, 1, 1), date(2023, 6, 30)),
    ('Mobile App Development', date(2023, 3, 1), date(2023, 12, 31)),
    ('Data Analytics Platform', date(2023, 5, 1), date(2024, 2, 28)),
    ('Customer Portal', date(2023, 7, 1), date(2023, 11, 30)),
]

cursor.executemany('INSERT OR IGNORE INTO projects (name, start_date, end_date) VALUES (?, ?, ?)', projects)

# Insert employee-project assignments
employee_projects = [
    (1, 1, 'Project Manager'),
    (2, 1, 'Developer'),
    (5, 1, 'Designer'),
    (1, 2, 'Lead Developer'),
    (2, 2, 'Developer'),
    (5, 2, 'QA Engineer'),
    (3, 3, 'Data Analyst'),
    (6, 3, 'Marketing Specialist'),
    (4, 4, 'Sales Lead'),
    (7, 4, 'Sales Associate'),
]

cursor.executemany('INSERT OR IGNORE INTO employee_projects (employee_id, project_id, role) VALUES (?, ?, ?)', employee_projects)

# Insert sample skills
skills = [
    ('Python',),
    ('JavaScript',),
    ('SQL',),
    ('Java',),
    ('C++',),
    ('Project Management',),
    ('Data Analysis',),
    ('Marketing',),
    ('Sales',),
    ('UI/UX Design',),
    ('DevOps',),
    ('Machine Learning',)
]

cursor.executemany('INSERT OR IGNORE INTO skills (name) VALUES (?)', skills)

# Insert employee-skill assignments with proficiency levels
employee_skills = [
    (1, 1, 'Expert'),  # John Doe - Python
    (1, 3, 'Advanced'),  # John Doe - SQL
    (1, 6, 'Advanced'),  # John Doe - Project Management
    (2, 1, 'Advanced'),  # Jane Smith - Python
    (2, 2, 'Intermediate'),  # Jane Smith - JavaScript
    (3, 7, 'Expert'),  # Bob Johnson - Data Analysis
    (3, 3, 'Advanced'),  # Bob Johnson - SQL
    (4, 9, 'Expert'),  # Alice Williams - Sales
    (4, 6, 'Intermediate'),  # Alice Williams - Project Management
    (5, 2, 'Advanced'),  # Charlie Brown - JavaScript
    (5, 10, 'Intermediate'),  # Charlie Brown - UI/UX Design
    (6, 8, 'Expert'),  # Diana Davis - Marketing
    (6, 7, 'Advanced'),  # Diana Davis - Data Analysis
    (7, 9, 'Advanced'),  # Eve Miller - Sales
]

cursor.executemany('INSERT OR IGNORE INTO employee_skills (employee_id, skill_id, proficiency_level) VALUES (?, ?, ?)', employee_skills)

# Generate random skills for additional employees
import random

# Get all skill ids
cursor.execute('SELECT id FROM skills')
skill_ids = [row[0] for row in cursor.fetchall()]

# Get all employee ids beyond the initial ones
cursor.execute('SELECT id FROM employees WHERE id > 7')
additional_employee_ids = [row[0] for row in cursor.fetchall()]

# Assign 1-4 random skills to each additional employee
for emp_id in additional_employee_ids:
    num_skills = random.randint(1, 4)
    selected_skills = random.sample(skill_ids, num_skills)
    for skill_id in selected_skills:
        proficiency = random.choice(['Beginner', 'Intermediate', 'Advanced', 'Expert'])
        try:
            cursor.execute('INSERT INTO employee_skills (employee_id, skill_id, proficiency_level) VALUES (?, ?, ?)',
                         (emp_id, skill_id, proficiency))
        except sqlite3.IntegrityError:
            # Skip if already exists (though unlikely)
            pass

# Commit changes and close connection
conn.commit()
conn.close()

print("Employee database updated successfully with 1007 employee records and skills!")