from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import openai
from fastapi.middleware.cors import CORSMiddleware


# os.environ.pop('OPENAI_API_KEY',None)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


app = FastAPI()

# origins = [
#     "http://localhost:3000",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslationRequest(BaseModel):
    phrase: str
    language: str  # 'hindi' or 'assamese'


# @app.post("/translate")
# async def translate_text(payload: dict):
#     print("Received:", payload)
#     return {"translated": "Hola"}  # Just testing


@app.post("/translate")
async def translate(request: TranslationRequest):
    prompt = f"""
You are a helpful and friendly language tutor.

User input: "{request.phrase}"
Language: {request.language.capitalize()}

Tasks:
1. Transliterate into the native script.
2. Translate to English.
3. Understand the context or emotion — Is this polite? casual? sarcastic? affectionate? angry?
4. Explain what the sentence means and how it's typically used in real conversations.
5. If it's idiomatic or has cultural meaning, explain that too.
6. Respond in a friendly and interactive way.

Output format:
- Script: [transliteration]
- Translation: [english]P
- Context: [context]
- Explanation: [explanation]
- Summary: [summary]
"""


    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        text = response.choices[0].message.content
        # Naively extract results
        def extract_between(label):
            if label + ": " in text:
                return text.split(label + ": ")[1].split("\n")[0].strip()
            return ""

        return {
            "script": extract_between("Script"),
            "translation": extract_between("Translation"),
            "explanation": extract_between("Explanation"),
            "summary": extract_between("Summary"),
        }
    except Exception as e:
        return {"error": str(e)}
