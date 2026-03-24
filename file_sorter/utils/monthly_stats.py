import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_NAME = os.path.join(DATA_DIR, "documents.db")

def connect_db():
    return sqlite3.connect(DB_NAME)

def get_monthly_stats(year=None, month=None):
    "Get file counts per letter_type for specific year/month or all time grouped by month."
    conn = connect_db()
    cursor = conn.cursor()
    
    if year and month:
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
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', date_added) as month,
                letter_type, 
                COUNT(*) as count
            FROM documents 
            GROUP BY month, letter_type
            ORDER BY month DESC, count DESC
        """)
        stats = cursor.fetchall()
        result = {}
        for month, letter_type, count in stats:
            if month not in result:
                result[month] = {}
            result[month][letter_type] = result[month].get(letter_type, 0) + count
        conn.close()
        return result

def get_total_scanned_per_month():
    "Total files per month."
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', date_added) as month, COUNT(*) as total
        FROM documents 
        GROUP BY month
        ORDER BY month DESC
    """)
    totals = cursor.fetchall()
    conn.close()
    return dict(totals)

def print_monthly_report(year=None, month=None):
    "Print formatted monthly stats report."
    if year and month:
        stats = get_monthly_stats(year, month)
    else:
        stats = get_monthly_stats()
    
    totals = get_total_scanned_per_month()
    
    report = "=== Monthly Scanned Files Statistics ===\\n"
    if totals:
        report += "Total files per month:\\n"
        for month, total in sorted(totals.items(), reverse=True):
            report += f"  {month}: {total} files\\n"
        report += "\\n"
    
    for month, categories in stats.items():
        report += f"{month} - Breakdown by category:\\n"
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            report += f"  {cat}: {count}\\n"
        report += "\\n"
    
    print(report)
    return report

# Example: print_monthly_report(2026, 3)

