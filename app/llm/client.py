from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.settings import GOOGLE_API_KEY


from langchain_openai import ChatOpenAI

from app.config.settings import OPENAI_API_KEY


def get_llm():
    return ChatOpenAI(
        model="gpt-5-nano",
        api_key=OPENAI_API_KEY,
        temperature=0,
    )