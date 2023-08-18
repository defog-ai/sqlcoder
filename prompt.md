### Instructions:
Your task is convert a question into a SQL query, given a Postgres database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float

### Input:
Generate a SQL query that answers the question `{user_question}`.
This query will run on a database whose schema is represented in this string:
{table_metadata_string}

### Response:
Based on your instructions, here is the SQL query I have generated to answer the question `{user_question}`:
```sql
