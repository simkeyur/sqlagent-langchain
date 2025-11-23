"""
Add email field to employees table with @datamint.app domain.
"""

import sqlite3

DB_PATH = "employee_database.db"

def add_email_column(conn):
    """Add email column to employees table if not exists"""
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE employees ADD COLUMN email TEXT UNIQUE")
        conn.commit()
        print("✅ Added email column to employees table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  email column already exists")
        else:
            raise

def generate_email(first_name, last_name, emp_id):
    """Generate email address based on name"""
    # Format: firstname.lastname@datamint.app
    email = f"{first_name.lower()}.{last_name.lower()}@datamint.app"
    return email

def populate_emails(conn):
    """Populate email addresses for all employees"""
    cursor = conn.cursor()
    
    # Get all employees
    cursor.execute("SELECT id, first_name, last_name FROM employees ORDER BY id")
    employees = cursor.fetchall()
    
    updated_count = 0
    for emp_id, first_name, last_name in employees:
        email = generate_email(first_name, last_name, emp_id)
        
        try:
            cursor.execute("UPDATE employees SET email = ? WHERE id = ?", (email, emp_id))
            updated_count += 1
        except sqlite3.IntegrityError:
            # Handle duplicate emails - add employee ID to make unique
            email = f"{first_name.lower()}.{last_name.lower()}.{emp_id}@datamint.app"
            cursor.execute("UPDATE employees SET email = ? WHERE id = ?", (email, emp_id))
            updated_count += 1
    
    conn.commit()
    print(f"✅ Added emails for {updated_count} employees")

def display_sample_emails(conn):
    """Display sample of emails"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📧 SAMPLE EMPLOYEE EMAILS")
    print("="*80)
    
    # Sample from each level
    cursor.execute("""
        SELECT e.first_name, e.last_name, e.email, eh.level, d.name
        FROM employees e
        JOIN employee_hierarchy eh ON e.id = eh.employee_id
        JOIN departments d ON e.department_id = d.id
        ORDER BY CASE eh.level
            WHEN 'CEO' THEN 1
            WHEN 'VP' THEN 2
            WHEN 'Director' THEN 3
            WHEN 'Manager' THEN 4
            WHEN 'IC' THEN 5
        END, d.name, e.id
        LIMIT 30
    """)
    
    print(f"\n{'Name':<25} {'Email':<40} {'Level':<10} {'Department':<20}")
    print("-" * 80)
    
    for first_name, last_name, email, level, dept in cursor.fetchall():
        name = f"{first_name} {last_name}"
        print(f"{name:<25} {email:<40} {level:<10} {dept:<20}")
    
    print("\n" + "="*80)

def display_email_statistics(conn):
    """Display email statistics"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 EMAIL STATISTICS")
    print("="*80)
    
    # Total emails
    cursor.execute("SELECT COUNT(*) FROM employees WHERE email IS NOT NULL")
    total_with_email = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]
    
    print(f"\n✅ Employees with email: {total_with_email} / {total_employees}")
    print(f"📧 Email domain: @datamint.app")
    
    # Emails by department
    print(f"\n{'Department':<20} {'Employees':<15}")
    print("-" * 35)
    
    cursor.execute("""
        SELECT d.name, COUNT(e.id) as count
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        WHERE e.email IS NOT NULL
        GROUP BY d.name
        ORDER BY count DESC
    """)
    
    for dept, count in cursor.fetchall():
        print(f"{dept:<20} {count:<15}")
    
    # Sample query
    print(f"\n{'Sample Query Results:'}")
    print("-" * 35)
    print("You can now query employees by email:")
    print('  Example: "Show me all employees with @datamint.app emails in Engineering"')
    print('  Example: "Find employees and their email addresses"')
    
    print("\n" + "="*80)

def main():
    """Main function"""
    print("🚀 Starting email field addition with @datamint.app domain...\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Add email column
        add_email_column(conn)
        
        # Populate emails
        populate_emails(conn)
        
        # Display samples
        display_sample_emails(conn)
        
        # Display statistics
        display_email_statistics(conn)
        
        print("✅ Email field successfully added and populated!")
        print(f"📁 Database location: {DB_PATH}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
