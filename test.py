from dotenv import load_dotenv
import os
import openai

load_dotenv()
key = os.getenv("OPENROUTER_API_KEY")
print("API key found:", bool(key))
print("Key starts with:", key[:12] if key else "No key found")

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=key
)

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hi"}],
        max_tokens=10
    )
    print("API call successful:", response.choices[0].message.content)
except Exception as e:
    print("API call failed:", str(e))