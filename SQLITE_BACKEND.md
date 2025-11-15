# SQLite Backend Support

## Overview

SQLite is now the **default database backend** for easy setup and development. No database server installation required!

## Configuration

### Default SQLite Setup

The application uses SQLite by default with this configuration in `.env`:

```ini
DATABASE_URL=sqlite:///./testtool.db
```

This creates a `testtool.db` file in the project root directory.

### Database File Locations

You can customize the SQLite database location:

```ini
# Relative path (in project directory)
DATABASE_URL=sqlite:///./testtool.db

# Absolute path
DATABASE_URL=sqlite:///C:/data/testtool.db

# In-memory database (testing only, data lost on restart)
DATABASE_URL=sqlite:///:memory:
```

## Quick Start

Use the SQLite start script:

```powershell
.\start_sqlite.ps1
```

This automatically:
1. Sets up virtual environment
2. Installs dependencies
3. Creates SQLite database
4. Runs migrations
5. Starts the server

## Switching Between SQLite and MySQL

### Use SQLite (Default)

```ini
DATABASE_URL=sqlite:///./testtool.db
```

### Use MySQL

1. Install MySQL drivers:
   ```powershell
   pip install pymysql cryptography
   ```

2. Create MySQL database:
   ```sql
   CREATE DATABASE testtool_db CHARACTER SET utf8mb4;
   ```

3. Update `.env`:
   ```ini
   DATABASE_URL=mysql+pymysql://user:password@localhost:3306/testtool_db
   ```

4. Run migrations:
   ```powershell
   alembic upgrade head
   ```

## Differences Between SQLite and MySQL

| Feature | SQLite | MySQL |
|---------|--------|-------|
| Setup | Zero configuration | Requires server installation |
| Performance | Fast for < 100k rows | Better for large datasets |
| Concurrency | Limited write concurrency | High concurrent writes |
| File-based | Yes (portable) | No (server-based) |
| Use Case | Development, small deployments | Production, high traffic |

## SQLite Advantages

✓ **No installation required** - Built into Python
✓ **Zero configuration** - Works out of the box
✓ **Portable** - Single file database
✓ **Fast for development** - Low latency
✓ **Perfect for testing** - Easy setup/teardown

## MySQL Advantages

✓ **Better concurrency** - Multiple writers
✓ **Scalability** - Handles millions of rows
✓ **Network access** - Remote connections
✓ **Advanced features** - Replication, clustering
✓ **Production-ready** - Enterprise support

## Migrations

Both backends use the same Alembic migrations:

```powershell
# Run all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current
```

The same migration files work for both SQLite and MySQL.

## File Management

### SQLite Database File

The SQLite database is stored as `testtool.db` in the project root.

**Backup**:
```powershell
cp testtool.db testtool.db.backup
```

**Delete and recreate**:
```powershell
rm testtool.db
alembic upgrade head
```

**Move to production**:
Just copy the `.db` file to the new location and update `DATABASE_URL`.

### .gitignore

SQLite database files are excluded from Git:
```
*.db
*.sqlite
*.sqlite3
```

## Testing

Tests work with both backends:

```powershell
# Run tests (uses in-memory SQLite by default)
pytest

# Run with specific backend
DATABASE_URL=sqlite:///./test.db pytest
```

## Performance Tips

### SQLite Optimization

Add to `.env` for better performance:
```ini
DATABASE_URL=sqlite:///./testtool.db?check_same_thread=False
```

### MySQL Optimization

Use connection pooling in production:
```ini
DATABASE_URL=mysql+pymysql://user:pass@host/db?charset=utf8mb4&pool_recycle=3600
```

## Troubleshooting

### SQLite Issues

**"database is locked"**
- SQLite has limited write concurrency
- Consider MySQL for high-traffic scenarios

**"no such table"**
- Run migrations: `alembic upgrade head`

### MySQL Issues

**"Can't connect to MySQL server"**
- Ensure MySQL is running
- Check host, port, credentials
- Install driver: `pip install pymysql cryptography`

## Recommendations

- **Development**: Use SQLite (default)
- **Small deployments** (< 10 users): SQLite is fine
- **Production** (> 10 concurrent users): Use MySQL
- **Testing**: SQLite with `:memory:`

## Summary

SQLite is now the default backend for **zero-configuration setup**. Switch to MySQL when you need production-scale concurrency and performance.

Quick commands:
```powershell
# Start with SQLite (default)
.\start_sqlite.ps1

# Start with MySQL
.\start.ps1
```

Both work seamlessly with the same codebase!
