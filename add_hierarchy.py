"""
Add salary data and manager hierarchy to the employee database.
Creates a realistic organizational structure: CEO -> VP -> Director -> Manager -> IC
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "employee_database.db"

# Salary ranges by level
SALARY_RANGES = {
    "CEO": (300000, 500000),
    "VP": (200000, 300000),
    "Director": (150000, 200000),
    "Manager": (100000, 150000),
    "IC": (50000, 120000),
}

# Department assignments for management levels
DEPARTMENTS = {
    "Engineering": {"Director": 1, "Manager": 3, "IC": 50},
    "Sales": {"Director": 1, "Manager": 4, "IC": 60},
    "Human Resources": {"Director": 1, "Manager": 2, "IC": 40},
    "Marketing": {"Director": 1, "Manager": 3, "IC": 50},
}

def create_hierarchy_table(conn):
    """Create hierarchy information table"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_hierarchy (
            employee_id INTEGER PRIMARY KEY,
            level TEXT NOT NULL,
            manager_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (manager_id) REFERENCES employees(id)
        )
    """)
    conn.commit()
    print("✅ Created employee_hierarchy table")

def add_salary_column(conn):
    """Add salary column to employees table if not exists"""
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE employees ADD COLUMN salary REAL")
        conn.commit()
        print("✅ Added salary column to employees table")
    except sqlite3.OperationalError:
        print("ℹ️  Salary column already exists")

def get_all_employees(conn):
    """Get all employees from database"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, department_id FROM employees ORDER BY id")
    return cursor.fetchall()

def get_department_name(conn, dept_id):
    """Get department name by ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM departments WHERE id = ?", (dept_id,))
    result = cursor.fetchone()
    return result[0] if result else "Unknown"

def create_hierarchy(conn):
    """Create organizational hierarchy"""
    employees = get_all_employees(conn)
    cursor = conn.cursor()
    
    # Clear existing hierarchy
    cursor.execute("DELETE FROM employee_hierarchy")
    
    # Create CEO (ID 1)
    ceo_id = employees[0][0]
    cursor.execute(
        "INSERT INTO employee_hierarchy (employee_id, level, manager_id) VALUES (?, ?, ?)",
        (ceo_id, "CEO", None)
    )
    cursor.execute("UPDATE employees SET salary = ? WHERE id = ?", 
                   (random.randint(*SALARY_RANGES["CEO"]), ceo_id))
    print(f"✅ Created CEO: Employee ID {ceo_id}")
    
    # Create VPs (one per department)
    vp_ids = []
    dept_count = 4
    vp_start_idx = 1
    for i in range(dept_count):
        vp_id = employees[vp_start_idx + i][0]
        vp_ids.append(vp_id)
        cursor.execute(
            "INSERT INTO employee_hierarchy (employee_id, level, manager_id) VALUES (?, ?, ?)",
            (vp_id, "VP", ceo_id)
        )
        cursor.execute("UPDATE employees SET salary = ? WHERE id = ?",
                       (random.randint(*SALARY_RANGES["VP"]), vp_id))
        dept_name = get_department_name(conn, employees[vp_start_idx + i][1])
        print(f"  ✅ Created VP ({dept_name}): Employee ID {vp_id}")
    
    # Create Directors per department (1 per dept, reports to VP)
    director_start_idx = vp_start_idx + dept_count
    director_ids = {}
    for i, vp_id in enumerate(vp_ids):
        director_id = employees[director_start_idx + i][0]
        director_ids[vp_id] = director_id
        cursor.execute(
            "INSERT INTO employee_hierarchy (employee_id, level, manager_id) VALUES (?, ?, ?)",
            (director_id, "Director", vp_id)
        )
        cursor.execute("UPDATE employees SET salary = ? WHERE id = ?",
                       (random.randint(*SALARY_RANGES["Director"]), director_id))
        dept_name = get_department_name(conn, employees[director_start_idx + i][1])
        print(f"    ✅ Created Director ({dept_name}): Employee ID {director_id}")
    
    # Create Managers (3-4 per director, reports to Director)
    manager_start_idx = director_start_idx + dept_count
    manager_idx = 0
    for director_id in director_ids.values():
        managers_count = random.randint(3, 4)
        for _ in range(managers_count):
            if manager_start_idx + manager_idx < len(employees):
                manager_id = employees[manager_start_idx + manager_idx][0]
                cursor.execute(
                    "INSERT INTO employee_hierarchy (employee_id, level, manager_id) VALUES (?, ?, ?)",
                    (manager_id, "Manager", director_id)
                )
                cursor.execute("UPDATE employees SET salary = ? WHERE id = ?",
                               (random.randint(*SALARY_RANGES["Manager"]), manager_id))
                manager_idx += 1
    
    print(f"  ✅ Created {manager_idx} Managers")
    
    # Create ICs (Individual Contributors) - rest of employees report to managers
    ic_start_idx = manager_start_idx + manager_idx
    manager_ids = []
    cursor.execute("SELECT employee_id FROM employee_hierarchy WHERE level = 'Manager'")
    manager_ids = [row[0] for row in cursor.fetchall()]
    
    ic_count = 0
    for idx in range(ic_start_idx, len(employees)):
        if manager_ids:
            ic_id = employees[idx][0]
            manager_id = random.choice(manager_ids)
            cursor.execute(
                "INSERT INTO employee_hierarchy (employee_id, level, manager_id) VALUES (?, ?, ?)",
                (ic_id, "IC", manager_id)
            )
            cursor.execute("UPDATE employees SET salary = ? WHERE id = ?",
                           (random.randint(*SALARY_RANGES["IC"]), ic_id))
            ic_count += 1
    
    print(f"  ✅ Created {ic_count} Individual Contributors")
    
    conn.commit()
    print(f"\n✅ Organizational hierarchy created successfully!")

def add_remaining_salaries(conn):
    """Add salaries to employees without hierarchy (if any)"""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees 
        SET salary = ? 
        WHERE salary IS NULL OR salary = 0
    """, (random.randint(*SALARY_RANGES["IC"]),))
    conn.commit()
    print("✅ Added default salaries to remaining employees")

def display_hierarchy_summary(conn):
    """Display hierarchy summary"""
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("📊 ORGANIZATIONAL HIERARCHY SUMMARY")
    print("="*70)
    
    cursor.execute("""
        SELECT level, COUNT(*) as count, 
               ROUND(AVG(e.salary), 0) as avg_salary,
               MIN(e.salary) as min_salary,
               MAX(e.salary) as max_salary
        FROM employee_hierarchy eh
        JOIN employees e ON eh.employee_id = e.id
        GROUP BY level
        ORDER BY CASE level
            WHEN 'CEO' THEN 1
            WHEN 'VP' THEN 2
            WHEN 'Director' THEN 3
            WHEN 'Manager' THEN 4
            WHEN 'IC' THEN 5
        END
    """)
    
    print(f"\n{'Level':<15} {'Count':<8} {'Avg Salary':<15} {'Min':<15} {'Max':<15}")
    print("-" * 70)
    
    for level, count, avg_sal, min_sal, max_sal in cursor.fetchall():
        print(f"{level:<15} {count:<8} ${avg_sal:>12,.0f} ${min_sal:>13,.0f} ${max_sal:>13,.0f}")
    
    # Salary by department
    print(f"\n{'Department':<20} {'Avg Salary':<15} {'Total Spend':<15}")
    print("-" * 50)
    
    cursor.execute("""
        SELECT d.name, 
               ROUND(AVG(e.salary), 0) as avg_salary,
               ROUND(SUM(e.salary), 0) as total_salary
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        GROUP BY d.name
        ORDER BY total_salary DESC
    """)
    
    for dept, avg_sal, total_sal in cursor.fetchall():
        print(f"{dept:<20} ${avg_sal:>13,.0f} ${total_sal:>13,.0f}")
    
    # Sample manager reporting structure
    print(f"\n{'Sample Manager Reporting Structure:'}")
    print("-" * 70)
    
    cursor.execute("""
        SELECT e.first_name, e.last_name, eh.level, m.first_name, m.last_name
        FROM employee_hierarchy eh
        JOIN employees e ON eh.employee_id = e.id
        LEFT JOIN employees m ON eh.manager_id = m.id
        WHERE eh.level IN ('Manager', 'Director', 'VP', 'CEO')
        LIMIT 10
    """)
    
    for emp_fname, emp_lname, level, mgr_fname, mgr_lname in cursor.fetchall():
        mgr_name = f"{mgr_fname} {mgr_lname}" if mgr_fname else "None (Root)"
        print(f"  {level:<10} {emp_fname} {emp_lname:<20} → {mgr_name}")
    
    print("\n" + "="*70)

def main():
    """Main function"""
    print("🚀 Starting database enhancement with salary and hierarchy data...")
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Add salary column
        add_salary_column(conn)
        
        # Create hierarchy table
        create_hierarchy_table(conn)
        
        # Create organizational structure
        create_hierarchy(conn)
        
        # Add salaries to any remaining employees
        add_remaining_salaries(conn)
        
        # Display summary
        display_hierarchy_summary(conn)
        
        print("\n✅ Database enhancement completed successfully!")
        print(f"📁 Database location: {DB_PATH}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
