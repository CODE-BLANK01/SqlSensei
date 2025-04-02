import os
from django.shortcuts import render
from django.db import connection
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load environment variables (make sure .env contains OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_database_schema():
    """
    Fetches the database schema (table names, column names, and data types).
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE();
        """)
        schema_info = cursor.fetchall()

    schema_dict = {}
    for table, column, dtype in schema_info:
        if table not in schema_dict:
            schema_dict[table] = []
        schema_dict[table].append(f"{column} ({dtype})")

    schema_text = "\n".join(
        [f"Table {table}: {', '.join(columns)}" for table, columns in schema_dict.items()]
    )
    return schema_text

def sql_query_view(request):
    if request.method == "POST":
        user_query = request.POST.get("query", "").strip()

        if not user_query:
            return render(request, "chat/query_form.html", {"error": "Please enter a query."})

        # Generate schema text
        schema_text = get_database_schema()

        # Prompt to send to LLM
        prompt = f"""
        You are an SQL expert. Convert the following natural language query into an SQL query.
        Use only the provided database schema.

        Schema:
        {schema_text}

        User Query: {user_query}

        SQL Query:
        """

        try:
            # Request to OpenAI's GPT model
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in SQL and database queries."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract SQL query from LLM response
            sql_query = response.choices[0].message.content.strip()


            # Strip triple backticks if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").strip("` \n")
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip("` \n")

            # Only allow safe queries for now
            if sql_query.lower().startswith(("select", "show", "describe","SELECT","SHOW","DESCRIBE")):
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()

                return render(request, "chat/query_form.html", {
                    "query": user_query,
                    "sql_query": sql_query,
                    "columns": columns,
                    "results": results
                })
            else:
                return render(request, "chat/query_form.html", {
                    "error": "Only SELECT queries are allowed for now.",
                    "sql_query": sql_query
                })

        except OpenAIError as e:
            return render(request, "chat/query_form.html", {"error": f"OpenAI Error: {str(e)}"})
        except Exception as e:
            return render(request, "chat/query_form.html", {"error": str(e)})

    return render(request, "chat/query_form.html")
