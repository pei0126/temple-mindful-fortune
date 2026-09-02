import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY', '').strip()
client = OpenAI(api_key=api_key, base_url='https://generativelanguage.googleapis.com/v1beta/openai/')

try:
    resp = client.chat.completions.create(
        model='gemini-3.1-flash-lite-preview',
        messages=[
            {'role': 'system', 'content': 'You are an empathetic counselor. Output valid JSON: {"message": "hello"}'},
            {'role': 'user', 'content': 'Say hello in Traditional Chinese'}
        ],
        response_format={'type': 'json_object'},
        temperature=0.7
    )
    print('SUCCESS! Response from Gemini 3.1 Flash-Lite Preview:')
    print(resp.choices[0].message.content)
except Exception as e:
    print('ERROR:', e)
