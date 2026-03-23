import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_NAME = os.path.join(DATA_DIR, "documents.db")

def connect_db():
    return sqlite3.connect(DB_NAME)

def get_monthly_stats(year=None, month=None):
    \"\"\"Get file counts per letter_type for specific year/month or all time grouped by month.\"\"\"
    conn = connect_db()
    cursor = conn.cursor()
    
    if year and month:
        # Specific month: total by type
        cursor.execute("""
            SELECT letter_type, COUNT(*) as count
            FROM documents 
            WHERE strftime('%Y', date_added) = ? AND strftime('%m', date_added) = ?
            GROUP BY letter_type
            ORDER BY count DESC
        """, (str(year), f'{month:02d}'))
        stats = cursor.fetchall()
        month_str = datetime(year, month, 1).strftime('%Y-%m')
        conn.close()
        return {month_str: dict(stats)}
    else:
        # All months: total per month
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', date_added) as month,
                letter_type, 
                COUNT(*) as count
            FROM documents 
            GROUP BY month, letter_type
            ORDER BY month DESC, count DESC
        ''')
        stats = cursor.fetchall()
        result = {}
        for month, letter_type, count in stats:
            if month not in result:
                result[month] = {}
            result[month][letter_type] = result[month].get(letter_type, 0) + count
        return result
    
    conn.close()

def get_total_scanned_per_month():
    \"\"\"Total files per month.\"\"\"
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT strftime('%Y-%m', date_added) as month, COUNT(*) as total
        FROM documents 
        GROUP BY month
        ORDER BY month DESC
    ''')
    totals = cursor.fetchall()
    conn.close()
    return dict(totals)

def print_monthly_report(year=None, month=None):
    \"\"\"Print formatted monthly stats report.\"\"\"
    if year and month:
        stats = get_monthly_stats(year, month)
        month_str = f\"{year}-{month:02d}\"
    else:
        stats = get_monthly_stats()
    
    totals = get_total_scanned_per_month()
    
    print("=== Monthly Scanned Files Statistics ===")
    if totals:
        print("Total files per month:")
        for month, total in sorted(totals.items(), reverse=True):
            print(f"  {month}: {total} files")
        print()
    
    for month, categories in stats.items():
        print(f"{month} - Breakdown by category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        print()

# Example usage:
# print_monthly_report(2026, 3)
# print_monthly_report()  # All months

