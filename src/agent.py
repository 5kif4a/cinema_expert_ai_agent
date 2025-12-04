from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import SYSTEM_PROMPT

from .tools import tools
from .memory import memory
from .llm import llm

__all__ = ("create_agent",)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


def create_agent(verbose: bool = False):
    """
    Create a cinema expert AI agent with function calling capabilities.

    Args:
        verbose: Enable verbose output to show agent's thinking process

    Returns:
        AgentExecutor instance configured with tools, memory, and LLM
    """
    agent = create_openai_functions_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=verbose,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )

    return agent_executor
