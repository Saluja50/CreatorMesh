from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.settings import GOOGLE_API_KEY


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )