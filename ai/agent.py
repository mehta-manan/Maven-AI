import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import trim_messages
from langchain.agents.middleware import before_model

from ai.prompt import sytem_prompt

llm = ChatOpenAI(model=str(os.getenv('LLM')))

trimmer = trim_messages(
    max_tokens=4096,
    strategy="last",
    token_counter=llm,
    include_system=True,
    allow_partial=False
)

# trim the messages before the agent calls the llm
@before_model
def trim_context(state, _runtime):
    return {
        "messages": trimmer.invoke(state['messages'])
    }

checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    system_prompt=sytem_prompt,
    checkpointer=checkpointer,
    middleware=[trim_context]
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