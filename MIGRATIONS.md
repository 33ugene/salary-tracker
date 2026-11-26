
# Database Migration Guide

## Purpose
This document describes how to safely update the database schema without losing existing user data.

## General Migration Procedure

1. Back up the existing `salary.db`.
2. Record the current row counts of all important tables.
3. Write the required SQL migration using ALTER TABLE or other appropriate SQL commands.
4. Test the migration on a copy of the existing database.
5. Verify that the database schema has been updated correctly.
6. Compare row counts before and after migration.
7. Test the application using the migrated database.
8. Keep the original backup until the migration is confirmed successful.

## Example: Adding session_version to users

### Migration SQL

```sql
ALTER TABLE users
ADD COLUMN session_version INTEGER NOT NULL DEFAULT 1;
```

### Verification

Check the table structure:

```sql
PRAGMA table_info(users);
```

Check existing data:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM income_records;
SELECT COUNT(*) FROM login_attempts;
```

Confirm that:
- The `session_version` column exists.
- Existing users have a default `session_version` of 1.
- Existing records are preserved.
- Row counts remain unchanged.

## Important Notes

- Never run an untested migration directly on the production database.
- Always create a backup before modifying the production database.
- `CREATE TABLE IF NOT EXISTS` does not modify existing tables.
