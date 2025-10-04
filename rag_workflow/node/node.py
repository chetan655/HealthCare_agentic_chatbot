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

def refiner(state: State) -> State:
    """This function refine the user query. remove ambiguity"""
    # print("refiner actiavted")
    question = state['query']
    # print("query -> ", question)
    try:
        chain = refiner_prompt | refiner_model 
        res = chain.invoke({'question': question})
        # print("res", res)
        # res = {'role': 'user', 'content': res.content}
        return {'messages': [res]}
    except Exception as e:
        return f"Error refining query: {e}"  # 
    # finally:
    #     print("refiner deactivated")
    

def classifier(state: State) -> State:
    """This function returns the category of the question."""
    # print("classifier actiavated")
    question = state['messages'][-1].content
    # print("this is classiier -> ", state['messages'])
    # print("question -> ", question)
    try: 
        chain = classifier_prompt | classifier_model 
        res = chain.invoke({'question': question})
        # print("response -> ", res)
        return {'category': res.category}
    except Exception as e:
        return f"Error classsifying question: {e}"
    # finally:
    #     print("classifier deactivated.")
    
def general_query_node(state: State) -> State:
    """This function returns answer to general query."""
    question = state['messages']   # last message later to change
    # print("question to general: ", question)
    try:
        chain = general_query_prompt | groq_llm_for_general_with_tools 
        res = chain.invoke({'question': question})
        # clean_res = sanitize_ai_message(ai_msg=res, keep_tool_calls=True)
        # print("output of res -> ", res)
        # print("output of clean_response -> ", clean_res)
        return {'messages': [res]}
    except Exception as e:
        return f"Error general_query_node: {e}"

