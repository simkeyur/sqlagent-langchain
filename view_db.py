import sqlite3

def view_database():
    conn = sqlite3.connect('employee_database.db')
    cursor = conn.cursor()

    # Show table counts
    tables = ['departments', 'employees', 'projects', 'employee_projects', 'skills', 'employee_skills']
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

    print("\nSample employees:")
    cursor.execute('''
        SELECT e.id, e.first_name, e.last_name, d.name as department,
               m.first_name || ' ' || m.last_name as manager
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN employees m ON e.manager_id = m.id
        LIMIT 10
    ''')
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]} {row[2]}, Dept: {row[3]}, Manager: {row[4] or 'None'}")

    print("\nSample projects with assignments:")
    cursor.execute('''
        SELECT p.name, COUNT(ep.employee_id) as employees_assigned
        FROM projects p
        LEFT JOIN employee_projects ep ON p.id = ep.project_id
        GROUP BY p.id, p.name
    ''')
    rows = cursor.fetchall()
    for row in rows:
        print(f"Project: {row[0]}, Employees: {row[1]}")

    print("\nSample employee skills:")
    cursor.execute('''
        SELECT e.first_name || ' ' || e.last_name as employee_name, s.name as skill, es.proficiency_level
        FROM employees e
        JOIN employee_skills es ON e.id = es.employee_id
        JOIN skills s ON es.skill_id = s.id
        LIMIT 15
    ''')
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}: {row[1]} ({row[2]})")

    conn.close()

if __name__ == "__main__":
    view_database()