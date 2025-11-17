from schema.schema import State
from prompts.prompt import (
    refiner_prompt, 
    classifier_prompt, 
    general_query_prompt,
    emergency_query_prompt,
    formatter_prompt,
    nearby_hospitals_prompt
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
        print("category -> ", res)
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
    

#==============================nearby hospitals node====================================

async def nearby_hospital_finder_node(state: State, config) -> State:
    """Finds the nearby hospitals."""
    print("nearby hospital node activate")
    question = state.get("question", "")
    summary = state.get("summary", "")

    try:
        chain = nearby_hospitals_prompt | groq_llm_for_general_with_tools
        res = await chain.ainvoke({"summary": summary, "question": question},config=config)
        return {"messages": [res]}
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

    # transcript_only = ""
    # if len(messages) >=1 :
    #     for i in messages:
    #         transcript_only += i.content

    transcript_parts = []

    # print("summary node activated")

    if messages:
        for m in messages:
            # get raw content (handle plain values or objects with .content)
            content = getattr(m, "content", m)

            # if content is a list, join elements; otherwise stringify
            if isinstance(content, list):
                transcript_parts.append(" ".join(str(c) for c in content))
            else:
                transcript_parts.append(str(content))

    transcript_only = " ".join(part for part in transcript_parts if part)

    if summary:
    # Update only when new information exists; otherwise return the old summary unchanged
        summary_msg = (
        f"Existing summary: {summary}\n\n"
        "Your task: Review the conversation above and determine whether it contains any "
        "new, changed, or corrected information that should be reflected in the summary.\n\n"
        "Rules:\n"
        "1. ONLY update the summary if truly new or modified information appears.\n"
        "2. If nothing new is present, RETURN THE EXISTING SUMMARY EXACTLY as-is.\n"
        "3. Keep the summary extremely concise but DO NOT remove or lose any important details.\n"
        "4. Preserve all essential facts, decisions, instructions, and outcomes.\n"
        "5. Do NOT add speculation, interpretations, or details not present in the conversation."
    )
    else:
    # No previous summary — create a new concise one
        summary_msg = (
        "Create an extremely concise summary of the entire conversation above. "
        "Include all essential information, decisions, facts, and outcomes, without adding anything extra."
    )

    # print(summary_msg)
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