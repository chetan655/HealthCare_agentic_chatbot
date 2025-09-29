from schema.schema import State
from prompts.prompt import refiner_prompt
from models.models import refiner_model

from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

def refiner(state: State) -> State:
    """This function refine the user query. remove ambiguity"""
    question = state['query']
    try:
        chain = refiner_prompt | refiner_model | parser
        res = chain.invoke(question)
        return {'messages': [res]}
    except Exception as e:
        return f"Error refining query: {e}"  # 
    
