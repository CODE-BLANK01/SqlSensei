from django.db import connection

def execute_sql_query(sql):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        return [["Error:", str(e)]]
