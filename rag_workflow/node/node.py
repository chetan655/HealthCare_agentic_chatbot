from schema.schema import State
from prompts.prompt import refiner_prompt, classifier_prompt, general_query_prompt
from models.models import refiner_model, classifier_model, base_model, base_model_with_tools, groq_llm_for_general_with_tools
# from utils import sanitize_ai_message

from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages.utils import (
    trim_messages,
    count_tokens_approximately
)

parser = StrOutputParser()

async def refiner(state: State) -> State:
    """This function refine the user query. remove ambiguity"""
    # print("refiner actiavted")
    question = state['query']
    # print("query -> ", question)
    try:
        chain = refiner_prompt | refiner_model 
        res = await chain.ainvoke({'question': question})
        # print("res", res)
        # res = {'role': 'user', 'content': res.content}
        return {'messages': [res]}
    except Exception as e:
        return {'error': f"Error refining query: {e}"}  # 
    # finally:
    #     print("refiner deactivated")
    

async def classifier(state: State) -> State:
    """This function returns the category of the question."""
    # print("classifier actiavated")
    # question = state['messages'][-1].content
    # print("this is classiier -> ", state['messages'])
    # print("question -> ", question)
    messages = state.get('messages', []) # Safely get messages
    if not messages:
        # Handle the case where there are no messages.
        # This could return a default category or raise a specific error.
        return {'category': 'general'} # Example: route to general if history is empty

    question = messages[-1].content
    try: 
        chain = classifier_prompt | classifier_model 
        res = await chain.ainvoke({'question': question})
        # print("response -> ", res)
        return {'category': res.category}
    except Exception as e:
        return {'error': f"Error refining query: {e}"}
    # finally:
    #     print("classifier deactivated.")
    
async def general_query_node(state: State, config) -> State:
    """This function returns answer to general query."""
    question = state['messages']   # last message later to change
    # print("question to general: ", question)
    messages = trim_messages(
        state['messages'],
        strategy='last',
        token_counter=count_tokens_approximately,
        max_tokens=50
    )
    # print("this is msgt -> ", messages)
    try:
        chain = general_query_prompt | groq_llm_for_general_with_tools 
        res = await chain.ainvoke({'question': messages}, config=config)
        """we only provide config to async model invoke if if python version < 3.11. this enable streaming"""
        # clean_res = sanitize_ai_message(ai_msg=res, keep_tool_calls=True)
        # print("output of res -> ", res)
        # print("output of clean_response -> ", clean_res)
        return {'messages': [res]}
    except Exception as e:
        return {'error': f"Error refining query: {e}"}