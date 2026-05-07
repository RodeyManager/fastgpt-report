"""Test API connection."""
import openai

client = openai.OpenAI(
    api_key='sk-kimi-2pJwB1zw2LL6YIFVUwlzOxLiDGlZAaYwgVkTX0bJVKcChQZ03uyAdcJABnOJEiTb',
    base_url='https://api.moonshot.cn/v1'
)

try:
    models = client.models.list()
    print('API OK, models:', [m.id for m in models.data[:3]])
except Exception as e:
    print('API Error:', e)
