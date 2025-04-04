import os
from django.shortcuts import redirect, render, get_object_or_404
from django.db import connection
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from users.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

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
    if "user_id" not in request.session:
        return redirect("login")
    user_id = request.session.get("user_id")
    user = User.objects.get(user_id = user_id)
    user_role = user.role.lower()

    if user_role == "student":
        url = "/users/student/dashboard/?show_home=true"
        allowed_queries = ("select", "show", "describe")  # Read-only queries
    elif user_role == "instructor":
        url = "/users/instructor/dashboard/?show_home=true"
        allowed_queries = ("select", "show", "describe", "insert", "update", "delete")  # Read + Write queries

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
        The current user is {user_id}

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
            if sql_query.lower().startswith((allowed_queries)):
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    if sql_query.lower().startswith("select"):
                        columns = [col[0] for col in cursor.description]
                        results = cursor.fetchall()
                    else:
                        columns = []
                        results = [("Query executed successfully.",)]
                
                request.session["query"] = user_query
                request.session["sql_query"] = sql_query
                request.session["columns"] = columns
                request.session["results"] = results
                
                
                return redirect(url)
            else:
                request.session["query"] = user_query
                request.session["sql_query"] = sql_query
                request.session["error"] = "Only SELECT queries are allowed for now."
                return redirect(url)

        except OpenAIError as e:
            request.session["query"] = user_query
            request.session["error"] = f"OpenAI Error: {str(e)}"
            return redirect(url)

        except Exception as e:
            request.session["query"] = user_query
            request.session["error"] = f"Error: {str(e)}"
            return redirect(url)

    return redirect(url)