### Task
Generate a SQL query to answer the following question:
`{user_question}`

### Database Schema
The query will run on a database with the following schema:
{table_metadata_string}

### SQL
Follow these steps to create the SQL Query:
1. Only use the columns and tables present in the database schema
2. Use table aliases to prevent ambiguity when doing joins. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.

Given the database schema, here is the SQL query that answers `{user_question}`:
```sql
