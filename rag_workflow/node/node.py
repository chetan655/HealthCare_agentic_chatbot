from schema.schema import State
from prompts.prompt import (
    refiner_prompt, 
    classifier_prompt, 
    general_query_prompt,
    emergency_query_prompt,
    formatter_prompt
)
from models.models import (
    refiner_model, classifier_model, 
    base_model, base_model_with_tools, 
    groq_llm_for_general_with_tools,
    summary_model
)
# from utils import sanitize_ai_message

from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages.utils import (
    trim_messages,
    count_tokens_approximately
)
from langchain_core.messages import RemoveMessage, HumanMessage, SystemMessage

parser = StrOutputParser()


#===========================refiner======================================

async def refiner(state: State) -> State:
    """This function refine the user query. remove ambiguity"""
    # print("refiner actiavted")
    question = state['question']
    # print("query -> ", question)
    try:
        chain = refiner_prompt | refiner_model 
        res = await chain.ainvoke({'question': question})
        print("res", res)
        # res = {'role': 'user', 'content': res.content}
        return {'messages': [res]}
    except Exception as e:
        return {'error': f"Error refining query: {e}"}  # 
    # finally:
    #     print("refiner deactivated")
    

#=========================================classifier==================================
async def classifier(state: State) -> State:
    """This function returns the category of the question."""

    question = state.get('question')
    try: 
        chain = classifier_prompt | classifier_model 
        res = await chain.ainvoke({'question': question})
        print("response -> ", res)
        return {'category': res.category, 'messages': [question]}
    except Exception as e:
        return {'error': f"Error refining query: {e}"}
    # finally:
    #     print("classifier deactivated.")



#==================================================general query===========================
    
async def general_query_node(state: State, config) -> State:
    """This function returns answer to general query."""
    print("general node activated.")
    question = state.get('question', "")
    summary = state.get("summary", "")
    # print("question to general: ", question)
    # messages = trim_messages(
    #     state['messages'],
    #     strategy='last',
    #     token_counter=count_tokens_approximately,
    #     max_tokens=100
    # )
    # print("this is msgt -> ", messages)
    try:
        chain = general_query_prompt | groq_llm_for_general_with_tools 
        res = await chain.ainvoke({"summary": summary, 'question': question}, config=config)
        """we only provide config to async model invoke if if python version < 3.11. this enable streaming"""
        # clean_res = sanitize_ai_message(ai_msg=res, keep_tool_calls=True)
        # print("output of res -> ", res)
        # print("output of clean_response -> ", clean_res)
        # print("res from general", res)
        return {'messages': [res]}
    except Exception as e:
        return {'error': f"Error refining query: {e}"}
    
    
    
#==============================emergency query node=====================================
    
async def emergency_query_node(state: State, config) -> State:
    """This function is to answer emergency quesions."""
    print("emergency node activated.")
    question = state.get("question", "")
    summary = state.get("summary", "")
    
    # messages = trim_messages(
    #     state['messages'],
    #     strategy='last',
    #     token_counter=count_tokens_approximately,
    #     max_tokens=100
    # )
    # print("this is msgt -> ", messages)
    try:
        chain = emergency_query_prompt | groq_llm_for_general_with_tools 
        res = await chain.ainvoke({"summary": summary, 'question': question}, config=config)
        # print("res from emergency", res)
        return {'messages': [res]}
    except Exception as e:
        return {'error': f"Error refining query: {e}"}
    


#=====================================summary======================================

async def summarize_conv(state: State) -> State:

    summary = state.get("summary", "")
    messages = state.get("messages", "")

    transcript_only = ""

    if len(messages) >=1 :
        for i in messages:
            transcript_only += i.content

    # print("this is transcript only", transcript_only)

    if summary:
    # Update only if new info exists, otherwise keep old summary
        summary_msg = (
        f"Here is the current short summary: {summary}\n\n"
        "Update it briefly to reflect ONLY new or changed information in above conversation transcript. "
        "If there are no updates, simply return the original summary unchanged. "
        "Keep it extremely concise and maintain all important info"
        )
    else:
    # No previous summary — create a new concise one
        summary_msg = "Create a very short, concise summary of the conversation above."



    # messages = [HumanMessage(content=transcript_only)] + [HumanMessage(content=summary_msg)]

    combined_msg = f"Conversation transcript: {transcript_only}\n\n {summary_msg}"
    messages = [
    HumanMessage(content=combined_msg),
    ]

    # print("this is msg", messages

    res = await summary_model.ainvoke(messages)

    # print("this is result", res)

    remaining_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-2]]

    return {"summary": res.content, "messages": remaining_messages}


#=====================================formatter node==========================

async def formatter_node(state: State) -> State:
    """takes tool results from format final user-facing messages."""
    # print("total messages -> ", state["messages"])
    messages = state["messages"][-2]
    question = state["question"]
    summary = state.get("summary", "")

    # print("result of formatter", messages)

    chain = formatter_prompt | base_model
    res = await chain.ainvoke({
        "recent_context": messages,
        "question": question,
        "summary": summary
    })
    return {"messages": [res]}