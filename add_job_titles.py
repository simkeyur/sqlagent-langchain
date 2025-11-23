"""
Add job_title field to employees table and populate based on hierarchy level.
"""

import sqlite3
import random

DB_PATH = "employee_database.db"

# Job titles by hierarchy level and department
JOB_TITLES = {
    "CEO": ["Chief Executive Officer"],
    "VP": {
        "Engineering": ["Vice President of Engineering", "VP Engineering"],
        "Sales": ["Vice President of Sales", "VP Sales"],
        "Human Resources": ["Vice President of HR", "VP Human Resources"],
        "Marketing": ["Vice President of Marketing", "VP Marketing"],
    },
    "Director": {
        "Engineering": ["Director of Engineering", "Engineering Director", "Director of Software Development"],
        "Sales": ["Director of Sales", "Sales Director", "Regional Sales Director"],
        "Human Resources": ["Director of Human Resources", "HR Director", "Talent Director"],
        "Marketing": ["Director of Marketing", "Marketing Director", "Content Director"],
    },
    "Manager": {
        "Engineering": ["Engineering Manager", "Senior Engineer", "Tech Lead Manager", "Dev Team Lead"],
        "Sales": ["Sales Manager", "Account Manager", "Territory Manager", "Sales Lead"],
        "Human Resources": ["HR Manager", "Talent Manager", "Recruiter Manager", "Employee Relations Manager"],
        "Marketing": ["Marketing Manager", "Campaign Manager", "Product Marketing Manager", "Brand Manager"],
    },
    "IC": {
        "Engineering": ["Software Engineer", "Junior Developer", "Senior Software Engineer", "Full Stack Developer", 
                        "Backend Engineer", "Frontend Engineer", "DevOps Engineer", "Database Engineer"],
        "Sales": ["Sales Representative", "Account Executive", "Sales Associate", "Business Development Specialist",
                  "Sales Consultant", "Inside Sales Representative"],
        "Human Resources": ["HR Specialist", "Recruiter", "HR Coordinator", "Talent Acquisition Specialist",
                           "Employee Relations Specialist", "Compensation Specialist"],
        "Marketing": ["Marketing Specialist", "Content Writer", "Social Media Manager", "Digital Marketing Specialist",
                      "Marketing Analyst", "Creative Designer", "Marketing Coordinator"],
    }
}

def add_job_title_column(conn):
    """Add job_title column to employees table if not exists"""
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE employees ADD COLUMN job_title TEXT")
        conn.commit()
        print("✅ Added job_title column to employees table")
    except sqlite3.OperationalError:
        print("ℹ️  job_title column already exists")

def populate_job_titles(conn):
    """Populate job titles based on hierarchy level and department"""
    cursor = conn.cursor()
    
    # Get all employees with their hierarchy level and department
    cursor.execute("""
        SELECT e.id, eh.level, d.name
        FROM employees e
        JOIN employee_hierarchy eh ON e.id = eh.employee_id
        JOIN departments d ON e.department_id = d.id
    """)
    
    employees = cursor.fetchall()
    
    updated_count = 0
    for emp_id, level, department in employees:
        if level == "CEO":
            job_title = JOB_TITLES["CEO"][0]
        elif level == "VP":
            titles = JOB_TITLES["VP"].get(department, ["Vice President"])
            job_title = random.choice(titles)
        elif level == "Director":
            titles = JOB_TITLES["Director"].get(department, ["Director"])
            job_title = random.choice(titles)
        elif level == "Manager":
            titles = JOB_TITLES["Manager"].get(department, ["Manager"])
            job_title = random.choice(titles)
        else:  # IC
            titles = JOB_TITLES["IC"].get(department, ["Individual Contributor"])
            job_title = random.choice(titles)
        
        cursor.execute("UPDATE employees SET job_title = ? WHERE id = ?", (job_title, emp_id))
        updated_count += 1
    
    conn.commit()
    print(f"✅ Updated job titles for {updated_count} employees")

def display_sample_job_titles(conn):
    """Display sample of job titles by level and department"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📋 SAMPLE JOB TITLES BY LEVEL AND DEPARTMENT")
    print("="*80)
    
    cursor.execute("""
        SELECT eh.level, d.name, e.first_name, e.last_name, e.job_title
        FROM employees e
        JOIN employee_hierarchy eh ON e.id = eh.employee_id
        JOIN departments d ON e.department_id = d.id
        WHERE eh.level IN ('CEO', 'VP', 'Director', 'Manager')
        ORDER BY CASE eh.level
            WHEN 'CEO' THEN 1
            WHEN 'VP' THEN 2
            WHEN 'Director' THEN 3
            WHEN 'Manager' THEN 4
        END, d.name, e.id
    """)
    
    print(f"\n{'Level':<12} {'Department':<20} {'Name':<25} {'Job Title':<40}")
    print("-" * 80)
    
    for level, dept, fname, lname, title in cursor.fetchall():
        name = f"{fname} {lname}"
        print(f"{level:<12} {dept:<20} {name:<25} {title:<40}")
    
    # Sample ICs
    print(f"\n{'Sample Individual Contributors:'}")
    print("-" * 80)
    
    cursor.execute("""
        SELECT d.name, e.first_name, e.last_name, e.job_title
        FROM employees e
        JOIN employee_hierarchy eh ON e.id = eh.employee_id
        JOIN departments d ON e.department_id = d.id
        WHERE eh.level = 'IC'
        ORDER BY d.name, e.id
        LIMIT 20
    """)
    
    current_dept = None
    for dept, fname, lname, title in cursor.fetchall():
        if dept != current_dept:
            print(f"\n{dept}:")
            current_dept = dept
        name = f"{fname} {lname}"
        print(f"  • {name:<25} → {title}")
    
    print("\n" + "="*80)

def display_job_title_statistics(conn):
    """Display job title statistics"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 JOB TITLE STATISTICS")
    print("="*80)
    
    # Count unique titles by level
    cursor.execute("""
        SELECT eh.level, COUNT(DISTINCT e.job_title) as unique_titles, COUNT(e.id) as total_employees
        FROM employees e
        JOIN employee_hierarchy eh ON e.id = eh.employee_id
        GROUP BY eh.level
        ORDER BY CASE eh.level
            WHEN 'CEO' THEN 1
            WHEN 'VP' THEN 2
            WHEN 'Director' THEN 3
            WHEN 'Manager' THEN 4
            WHEN 'IC' THEN 5
        END
    """)
    
    print(f"\n{'Level':<12} {'Unique Titles':<18} {'Total Employees':<18}")
    print("-" * 50)
    
    for level, unique, total in cursor.fetchall():
        print(f"{level:<12} {unique:<18} {total:<18}")
    
    # Most common titles
    print(f"\n{'Most Common Job Titles:'}")
    print("-" * 50)
    
    cursor.execute("""
        SELECT job_title, COUNT(*) as count
        FROM employees
        WHERE job_title IS NOT NULL
        GROUP BY job_title
        ORDER BY count DESC
        LIMIT 10
    """)
    
    for i, (title, count) in enumerate(cursor.fetchall(), 1):
        print(f"{i:>2}. {title:<40} ({count} employees)")
    
    print("\n" + "="*80)

def main():
    """Main function"""
    print("🚀 Starting job title field addition...")
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Add job_title column
        add_job_title_column(conn)
        
        # Populate job titles
        populate_job_titles(conn)
        
        # Display samples
        display_sample_job_titles(conn)
        
        # Display statistics
        display_job_title_statistics(conn)
        
        print("\n✅ Job title field successfully added and populated!")
        print(f"📁 Database location: {DB_PATH}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
