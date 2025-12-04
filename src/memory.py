from langchain.memory import ConversationSummaryBufferMemory
from .llm import llm
from .config import MAX_TOKENS

memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True,
    output_key="output",
    max_token_limit=MAX_TOKENS,
)
