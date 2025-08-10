# import openai
# import os
# from dotenv import load_dotenv


# load_dotenv()
# # print("API Key Loaded:", os.getenv("OPENROUTER_API_KEY"))


# client = openai.OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=os.getenv("OPENROUTER_API_KEY"),
# )

# def ask_ai(question, language):
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",  
#         messages=[
#             {"role": "system", "content": f"You are a friendly {language.capitalize()} tutor who explains things in simple ways with examples."},
#             {"role": "user", "content": question}
#         ],
#         max_tokens=524
#     )
    
#     return response.choices[0].message.content

import openai
import os
from dotenv import load_dotenv

load_dotenv()
# print("API Key Loaded:", os.getenv("OPENROUTER_API_KEY"))

client = openai.OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

def ask_ai(question, language):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": f"You are a friendly {language.capitalize()} tutor who explains things in simple ways with examples."},
            {"role": "user", "content": question}
        ],
        max_tokens=524
    )
    
    return response.choices[0].message.content
