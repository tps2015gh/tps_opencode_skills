---
name: mysql-query
description: Execute MySQL queries from natural language and display results as formatted tables.
version: 1.0.0
author: MiMo V2 Pro Free (OpenCode)
tags: [database, mysql, sql, query, table]
---

# MySQL Query Skill

Execute SQL queries on MySQL databases and display results as formatted tables.

---

## For AI Agent

### When to Use This Skill
- User asks to query data from MySQL database
- User wants to see data in table format
- User asks "show me...", "how many...", "list all..." from database

### How to Use
1. Translate user's natural language to SQL query
2. Execute: `python .opencode/skills/mysql-query/mysql_query.py query "SELECT ..."`
3. Display results to user

### Example Translations

| User Says | SQL Query |
|-----------|-----------|
| Show all users | `SELECT * FROM users LIMIT 20` |
| How many orders today? | `SELECT COUNT(*) FROM orders WHERE DATE(created)=CURDATE()` |
| List active products | `SELECT id, name, price FROM products WHERE status='active'` |
| Show recent logins | `SELECT * FROM login_log ORDER BY created_at DESC LIMIT 10` |
| Total sales this month | `SELECT SUM(amount) FROM sales WHERE MONTH(created)=MONTH(CURDATE())` |

### Commands
```bash
# Setup mysql.exe path (one time)
python .opencode/skills/mysql-query/mysql_query.py setup "C:\path\to\mysql.exe"

# Connect to database (prompts for credentials)
python .opencode/skills/mysql-query/mysql_query.py connect

# Run query
python .opencode/skills/mysql-query/mysql_query.py query "SELECT * FROM users"

# Show current config
python .opencode/skills/mysql-query/mysql_query.py config
```

---

## For Human User

### Installation

1. Copy `.opencode/skills/mysql-query/` folder to your project
2. Ensure MySQL is installed on your system

### First Time Setup

**Step 1: Set mysql.exe path**
```bash
python .opencode/skills/mysql-query/mysql_query.py setup "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
```

**Step 2: Connect to database**
```bash
python .opencode/skills/mysql-query/mysql_query.py connect
```
You will be prompted:
```
🔧 MySQL Connection Setup
──────────────────────────────
Host [localhost]: 
Port [3306]: 
Username [root]: 
Password: ********
Database name: mydb

✅ Connected: root@localhost:3306/mydb
   (Credentials saved to session only, not to file)
```

### Running Queries

```bash
# Simple query
python .opencode/skills/mysql-query/mysql_query.py query "SHOW TABLES"

# With conditions
python .opencode/skills/mysql-query/mysql_query.py query "SELECT id, name FROM users WHERE status=1"

# Aggregation
python .opencode/skills/mysql-query/mysql_query.py query "SELECT COUNT(*) as total FROM orders"
```

### Example Output

```
📝 Query: SELECT id, name, email FROM users LIMIT 3

+----+--------+-------------------+
| id | name   | email             |
+----+--------+-------------------+
| 1  | John   | john@example.com  |
| 2  | Jane   | jane@example.com  |
| 3  | Bob    | bob@example.com   |
+----+--------+-------------------+
(3 rows)
```

---

## Security

- **Passwords are NOT saved to file** - only stored in session memory
- Connection credentials are cleared when process ends
- Only `mysql.exe` path is saved to `mysql_config.json`

---

## Files

| File | Description |
|------|-------------|
| `mysql_query.py` | Main script - execute queries and format output |
| `mysql_config.json` | Stores only mysql.exe path (auto-generated) |
| `SKILL.md` | This documentation file |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| mysql.exe not found | Run `setup` with correct path |
| Access denied | Check username/password |
| Unknown database | Check database name in `connect` |
| Query timeout | Add LIMIT to large queries |
