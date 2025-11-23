import sqlite3
import random

# Connect to SQLite database
conn = sqlite3.connect('employee_database.db')
cursor = conn.cursor()

# Create skills table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
''')

# Create employee_skills table if not exists
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

# Insert employee-skill assignments with proficiency levels for initial employees
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

# Generate random skills for all employees
# Get all skill ids
cursor.execute('SELECT id FROM skills')
skill_ids = [row[0] for row in cursor.fetchall()]

# Get all employee ids
cursor.execute('SELECT id FROM employees')
employee_ids = [row[0] for row in cursor.fetchall()]

# Assign 1-4 random skills to each employee (skip if already has skills)
for emp_id in employee_ids:
    # Check if employee already has skills
    cursor.execute('SELECT COUNT(*) FROM employee_skills WHERE employee_id = ?', (emp_id,))
    if cursor.fetchone()[0] > 0:
        continue  # Skip if already has skills

    num_skills = random.randint(1, 4)
    selected_skills = random.sample(skill_ids, num_skills)
    for skill_id in selected_skills:
        proficiency = random.choice(['Beginner', 'Intermediate', 'Advanced', 'Expert'])
        cursor.execute('INSERT INTO employee_skills (employee_id, skill_id, proficiency_level) VALUES (?, ?, ?)',
                     (emp_id, skill_id, proficiency))

# Commit changes and close connection
conn.commit()
conn.close()

print("Skills added to employee database successfully!")