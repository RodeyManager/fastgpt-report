"""Test DeepSeek API connection."""
import openai

client = openai.OpenAI(
    api_key='sk-aaffcda6bd1a426f9df20c344d3394f7',
    base_url='https://api.deepseek.com'
)

try:
    response = client.chat.completions.create(
        model='deepseek-v4-pro',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=10
    )
    print('API OK:', response.choices[0].message.content)
except Exception as e:
    print('API Error:', e)
