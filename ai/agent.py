import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from ai.prompt import sytem_prompt

llm = ChatOpenAI(model=str(os.getenv('LLM')))

checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    system_prompt=sytem_prompt,
    checkpointer=checkpointer
)

def generate_reply(sender_id, message):
    result = agent.invoke(
        {
            "messages": [{
                "role": "user",
                "content": message
            }]
        },
        config={
            "configurable": {
                "thread_id": sender_id
            }
        }
    )
    
    return result['messages'][-1].content