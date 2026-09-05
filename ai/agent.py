import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from ai.prompt import sytem_prompt

llm = ChatOpenAI(model=str(os.getenv('LLM')))

agent = create_agent(
    model=llm,
    system_prompt=sytem_prompt
)

def generate_reply(message):
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": message
        }]
    })
    
    return result['messages'][-1].content