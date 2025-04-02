import openai
from decouple import config

openai.api_key = config('OPENAI_API_KEY')

def translate_to_sql(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI tutor that converts natural language to SQL queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300
    )
    return response.choices[0].message['content'].strip()
