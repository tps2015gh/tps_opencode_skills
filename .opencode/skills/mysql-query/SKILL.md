---
name: mysql-query
description: Execute MySQL queries using Python connector (no mysql.exe needed).
version: 2.0.0
author: MiMo V2 Pro Free (OpenCode)
tags: [database, mysql, sql, query, table]
---

# MySQL Query Skill

Execute SQL queries on MySQL databases using Python - no mysql.exe required!

## Install Dependency

```bash
pip install mysql-connector-python
```

(Or it auto-installs on first run)

---

## For AI Agent

### When to Use
- User asks to query data from MySQL database
- User wants to see data in table format

### Commands
```bash
# Connect (prompts for credentials)
python .opencode/skills/mysql-query/mysql_query.py connect

# Run query
python .opencode/skills/mysql-query/mysql_query.py query "SELECT * FROM users"

# Show config
python .opencode/skills/mysql-query/mysql_query.py config
```

### Natural Language → SQL Examples

| User Says | SQL Query |
|-----------|-----------|
| Show all users | `SELECT * FROM users LIMIT 20` |
| How many orders today? | `SELECT COUNT(*) FROM orders WHERE DATE(created)=CURDATE()` |
| List active products | `SELECT id, name, price FROM products WHERE status='active'` |
| Total sales this month | `SELECT SUM(amount) FROM sales WHERE MONTH(created)=MONTH(CURDATE())` |

---

## For Human User

### First Time

```bash
# Connect to database (prompts for host, user, pass, db)
python .opencode/skills/mysql-query/mysql_query.py connect
```

You will see:
```
🔧 MySQL Connection Setup
──────────────────────────────
Host [localhost]: 
Port [3306]: 
Username [root]: 
Password: ********
Database name: mydb

✅ Connected: root@localhost:3306/mydb
```

### Run Queries

```bash
python .opencode/skills/mysql-query/mysql_query.py query "SHOW TABLES"
python .opencode/skills/mysql-query/mysql_query.py query "SELECT id, name FROM users LIMIT 5"
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

- **No mysql.exe needed** - uses Python connector
- **Passwords NOT saved** - only in session memory
- Credentials cleared when process ends

---

## Files

| File | Description |
|------|-------------|
| `mysql_query.py` | Main script |
| `SKILL.md` | This documentation |
