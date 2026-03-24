#!/usr/bin/env python3
"""MySQL Query - Execute SQL queries and display results as table"""

import os
import sys
import json
import subprocess
import getpass

# Session config (not saved to file)
SESSION_CONFIG = {}


def load_config():
    """Load MySQL config - mysql_path from file, credentials from session"""
    config_file = os.path.join(os.path.dirname(__file__), 'mysql_config.json')
    file_config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            file_config = json.load(f)
    
    # Merge: session overrides file
    config = {**file_config, **SESSION_CONFIG}
    return config


def save_config(config):
    """Save only mysql_path to file, credentials stay in session"""
    config_file = os.path.join(os.path.dirname(__file__), 'mysql_config.json')
    safe_config = {'mysql_path': config.get('mysql_path', '')}
    with open(config_file, 'w') as f:
        json.dump(safe_config, f, indent=2)


def setup_mysql_path(mysql_path):
    """Setup mysql.exe path"""
    if not os.path.exists(mysql_path):
        print(f"Error: mysql.exe not found at: {mysql_path}")
        return False
    
    save_config({'mysql_path': mysql_path})
    print(f"✅ MySQL path saved: {mysql_path}")
    return True


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
    
    password = getpass.getpass("Password: ")
    
    database = input("Database name: ").strip()
    
    SESSION_CONFIG = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }
    
    print(f"\n✅ Connected: {user}@{host}:{port}/{database}")
    print("   (Credentials in session only, not saved to file)")


def execute_query(sql_query):
    """Execute SQL query and return results"""
    config = load_config()
    
    mysql_path = config.get('mysql_path')
    if not mysql_path or not os.path.exists(mysql_path):
        print("Error: mysql.exe not configured. Run setup first.")
        return None
    
    if not config.get('user') or not config.get('database'):
        print("Error: Not connected. Run connect first.")
        return None
    
    host = config.get('host', 'localhost')
    user = config.get('user')
    password = config.get('password', '')
    database = config.get('database')
    port = config.get('port', '3306')
    
    cmd = [mysql_path, f'-h{host}', f'-P{port}', f'-u{user}']
    if password:
        cmd.append(f'-p{password}')
    cmd.extend(['--batch', '--raw', '-e', sql_query, database])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            error = result.stderr.replace(password, '***') if password else result.stderr
            print(f"MySQL Error: {error}")
            return None
        
        return result.stdout
    except subprocess.TimeoutExpired:
        print("Error: Query timed out (30s)")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def format_table(raw_output):
    """Format MySQL batch output as table"""
    if not raw_output or not raw_output.strip():
        return "No results"
    
    lines = raw_output.strip().split('\n')
    if len(lines) < 1:
        return "No results"
    
    header = lines[0].split('\t')
    data = []
    for line in lines[1:]:
        if line.strip():
            row = line.split('\t')
            data.append(row)
    
    if not data:
        return "No data rows"
    
    col_widths = [len(h) for h in header]
    for row in data:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    header_row = '|' + '|'.join(f' {h:<{col_widths[i]}} ' for i, h in enumerate(header)) + '|'
    
    table_lines = [separator, header_row, separator]
    for row in data:
        row_line = '|' + '|'.join(f' {str(row[i]) if i < len(row) else "":<{col_widths[i]}} ' for i in range(len(col_widths))) + '|'
        table_lines.append(row_line)
    table_lines.append(separator)
    table_lines.append(f"({len(data)} rows)")
    
    return '\n'.join(table_lines)


def run_query(sql_query):
    """Run query and display formatted table"""
    print(f"\n📝 Query: {sql_query}\n")
    
    raw = execute_query(sql_query)
    if raw is None:
        return
    
    table = format_table(raw)
    print(table)


def show_config():
    """Show current configuration"""
    config = load_config()
    print("\n📋 MySQL Config:")
    print(f"  mysql_path: {config.get('mysql_path', '❌ Not set')}")
    if SESSION_CONFIG:
        print(f"  host: {SESSION_CONFIG.get('host', '-')}")
        print(f"  user: {SESSION_CONFIG.get('user', '-')}")
        print(f"  database: {SESSION_CONFIG.get('database', '-')}")
        print(f"  port: {SESSION_CONFIG.get('port', '-')}")
        print("  password: ********")
    else:
        print("  Session: Not connected (run connect first)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('MySQL Query Tool')
        print('================')
        print('')
        print('Usage:')
        print('  python mysql_query.py setup <path_to_mysql.exe>')
        print('  python mysql_query.py connect')
        print('  python mysql_query.py query "SELECT * FROM table"')
        print('  python mysql_query.py config')
        print('')
        print('Examples:')
        print('  python mysql_query.py setup "C:\\mysql\\bin\\mysql.exe"')
        print('  python mysql_query.py connect')
        print('  python mysql_query.py query "SHOW TABLES"')
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == 'setup':
        if len(sys.argv) < 3:
            print('Usage: python mysql_query.py setup <path_to_mysql.exe>')
            sys.exit(1)
        setup_mysql_path(sys.argv[2])
    
    elif mode == 'connect':
        prompt_connection()
    
    elif mode == 'query':
        if len(sys.argv) < 3:
            print('Usage: python mysql_query.py query "SELECT * FROM table"')
            sys.exit(1)
        run_query(sys.argv[2])
    
    elif mode == 'config':
        show_config()
    
    else:
        print(f'Unknown mode: {mode}')
        print('Use: setup, connect, query, or config')
        sys.exit(1)
