from langchain_openai import ChatOpenAI
from src.config import MODEL_NAME, TEMPERATURE, OPENAI_API_KEY

llm = ChatOpenAI(
    model=MODEL_NAME, temperature=TEMPERATURE, openai_api_key=OPENAI_API_KEY
)
