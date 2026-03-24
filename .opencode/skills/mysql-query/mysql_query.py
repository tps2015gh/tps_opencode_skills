#!/usr/bin/env python3
"""MySQL Query - Execute SQL queries using Python connector (no mysql.exe needed)"""

import os
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Session config (not saved to file)
SESSION_CONFIG = {}


def check_connector():
    """Check if mysql-connector-python is installed"""
    try:
        import mysql.connector
        return True
    except ImportError:
        print("mysql-connector-python not installed.")
        print("Installing...")
        os.system('pip install mysql-connector-python')
        try:
            import mysql.connector
            return True
        except ImportError:
            print("Failed to install. Run: pip install mysql-connector-python")
            return False


def prompt_connection():
    """Prompt user for connection details"""
    global SESSION_CONFIG
    
    print("\n🔧 MySQL Connection Setup")
    print("─" * 30)
    
    host = input("Host [localhost]: ").strip()
    if not host:
        host = 'localhost'
    
    port = input("Port [3306]: ").strip()
    if not port:
        port = '3306'
    
    user = input("Username [root]: ").strip()
    if not user:
        user = 'root'
    
    import getpass
    password = getpass.getpass("Password: ")
    
    database = input("Database name: ").strip()
    
    SESSION_CONFIG = {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password,
        'database': database
    }
    
    print(f"\n✅ Connected: {user}@{host}:{port}/{database}")
    print("   (Credentials in session only, not saved to file)")


def execute_query(sql_query):
    """Execute SQL query using mysql-connector"""
    import mysql.connector
    
    if not SESSION_CONFIG:
        print("Error: Not connected. Run connect first.")
        return None, None
    
    try:
        conn = mysql.connector.connect(
            host=SESSION_CONFIG['host'],
            port=SESSION_CONFIG['port'],
            user=SESSION_CONFIG['user'],
            password=SESSION_CONFIG['password'],
            database=SESSION_CONFIG['database']
        )
        
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Get data
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return columns, data
        
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def format_table(columns, data):
    """Format query results as table"""
    if not columns:
        return "Query executed successfully (no data)"
    
    if not data:
        return "No data rows"
    
    # Convert all data to strings
    str_data = [[str(cell) if cell is not None else 'NULL' for cell in row] for row in data]
    
    # Calculate column widths
    col_widths = [len(col) for col in columns]
    for row in str_data:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))
    
    # Build table
    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    header_row = '|' + '|'.join(f' {col:<{col_widths[i]}} ' for i, col in enumerate(columns)) + '|'
    
    table_lines = [separator, header_row, separator]
    for row in str_data:
        row_line = '|' + '|'.join(f' {row[i]:<{col_widths[i]}} ' for i in range(len(col_widths))) + '|'
        table_lines.append(row_line)
    table_lines.append(separator)
    table_lines.append(f"({len(data)} rows)")
    
    return '\n'.join(table_lines)


def run_query(sql_query):
    """Run query and display formatted table"""
    print(f"\n📝 Query: {sql_query}\n")
    
    columns, data = execute_query(sql_query)
    if columns is None and data is None:
        return
    
    table = format_table(columns, data)
    print(table)


def show_config():
    """Show current configuration"""
    print("\n📋 MySQL Config:")
    print(f"  host: {SESSION_CONFIG.get('host', '❌ Not connected')}")
    print(f"  port: {SESSION_CONFIG.get('port', '-')}")
    print(f"  user: {SESSION_CONFIG.get('user', '-')}")
    print(f"  database: {SESSION_CONFIG.get('database', '-')}")
    print(f"  password: {'********' if SESSION_CONFIG.get('password') else '-'}")


if __name__ == '__main__':
    if not check_connector():
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print('MySQL Query Tool')
        print('================')
        print('')
        print('Usage:')
        print('  python mysql_query.py connect <host> <user> <password> <database> [port]')
        print('  python mysql_query.py query "SELECT * FROM table"')
        print('  python mysql_query.py config')
        print('')
        print('Examples:')
        print('  python mysql_query.py connect localhost root mypass mydb')
        print('  python mysql_query.py connect 192.168.1.100 admin secret shopdb 3307')
        print('  python mysql_query.py query "SHOW TABLES"')
        print('  python mysql_query.py query "SELECT * FROM users LIMIT 10"')
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == 'connect':
        if len(sys.argv) < 6:
            print('Usage: python mysql_query.py connect <host> <user> <password> <database> [port]')
            print('')
            print('Examples:')
            print('  python mysql_query.py connect localhost root mypass mydb')
            print('  python mysql_query.py connect 192.168.1.100 admin secret shopdb 3307')
            sys.exit(1)
        host = sys.argv[2]
        user = sys.argv[3]
        password = sys.argv[4]
        database = sys.argv[5]
        port = int(sys.argv[6]) if len(sys.argv) > 6 else 3306
        
        SESSION_CONFIG = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        print(f"✅ Connected: {user}@{host}:{port}/{database}")
    
    elif mode == 'query':
        if len(sys.argv) < 3:
            print('Usage: python mysql_query.py query "SELECT * FROM table"')
            sys.exit(1)
        run_query(sys.argv[2])
    
    elif mode == 'config':
        show_config()
    
    else:
        print(f'Unknown mode: {mode}')
        print('Use: connect, query, or config')
        sys.exit(1)
