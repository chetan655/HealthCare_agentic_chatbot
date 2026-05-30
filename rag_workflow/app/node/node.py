import os
import base64
import json
from io import BytesIO
from dotenv import load_dotenv

# import google.genai as genai


from typing import Dict, Any
from PIL import Image, ImageOps
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from langchain_core.runnables import Runnable

from app.schema.schema import State
from app.services.embedding_service import LocalEmbeddingService
from app.services.pinecone_service import PineconeService


from app.prompts.prompt import (
    classifier_prompt,
    general_prompt,
    general_prompt1,
    general_prompt_formatter,
    nearby_hospitals_prompt,
    formatter_prompt,
    hospital_formatter_prompt,
    image_ocr_prompt,
    ocr_formatter_prompt
)

from app.models.model import (
    classifier_model,
    # flash_2_5,
    groq_llm,
    groq_llm_with_tools
)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# genai.configure(api_key=GOOGLE_API_KEY)



# python is sync by default but can also act as async using asyncio
# asyncio is python lib used to write non-blocking code

###################classifier########################
async def classifier(state: State) -> State:
    """Returns the category of the question."""

    print("classifier node active")

    question = state.get("question", "")
    summary = state.get("summary", "")
    
    has_image = bool(state.get("image"))

    # print("this is state", state)


    try:
        chain = classifier_prompt | classifier_model
        res = await chain.ainvoke({'question': question, "summary": summary, 'has_image': has_image})
        print("this is category: ", res)
        return {'category': res.category, 'messages': [question]}
    except Exception as e:
        print("error at classifier:", e)
        # raise e
        # return {'error': f"Error catogarizing: {e}"}

##################general###########################
async def general(state: State):
    """Returns answer to general query."""

    print("general node active")

    summary = state.get("summary", "")
    question = state.get("question", "")
    retrieved_docs = state.get("memory_docs", "")


    try:
        chain = general_prompt1 | groq_llm
        res = await chain.ainvoke({"question": question, "summary": summary, "retrieved_docs": retrieved_docs})
        # print("this is res", res)
        return {"messages": [res]}
    except Exception as e:
        print("error at general", e)
        # raise e
    
    # finally:
    #     print("this is from messages: ", state["messages"])


##################33 general formatter #######################

async def general_formatter(state: State) -> State:

    print("general formatter active")

    summary = state.get("summary", "")
    question = state.get("question", "")
    retrieved_docs = state.get("memory_docs", "")
    tool_result = state["messages"][-1]

    chain = general_prompt_formatter | groq_llm
    res = await chain.ainvoke({
        "summary": summary,
        "question": question,
        "retrieved_docs": retrieved_docs,
        "tool_result": tool_result
    })
    return {"messages": [res]}



async def find_nearby_hospitals(state: State):
    """node to find nearby hospitals"""

    print("find nearby hospitals node active")

    question = state.get("question")
    
    lat = str(state.get("lat", ""))
    long = str(state.get("long", ""))

    print("lat and long at hos", lat, long, question)



    try:
        chain = nearby_hospitals_prompt | groq_llm_with_tools
        res = await chain.ainvoke({
            "question": question,
            "lat": lat,
            "long": long
        })
        # print("this is response of nearby hosptials: ", res)
        return {"messages": [res]}
    except Exception as e:
        print(f"error finding hospitals: {e}")


####################33 formatter node ##################################

async def formatter_node(state: State) -> State:
    """Generate the final response."""

    print("formatter node active")

    messages = state["messages"][-2:]
    question = state["question"]
    summary = state.get("summary", "")

    chain = formatter_prompt | groq_llm
    res = await chain.ainvoke({
        "recent_context": messages,
        "question": question,
        "summary": summary
    })

    print("this is response of formatter: ", res)
    return {"messages": [res]}


######################## hospital formatter ###################3
async def hospital_formatter(state: State) -> State:
    """Generte final respone for finding nearby hospitals."""

    print("hospital formatter node active")

    question = state["question"]
    tool_data = state["messages"][-1]

    chain = hospital_formatter_prompt | groq_llm
    res = await chain.ainvoke({
        "question": question,
        "tool_result": tool_data
    })
    return {"messages": [res]}



#####################333 ocr node ########################3

# async def oc_node(state: State) -> State:
    
#     summary = state.get("summary", "")
#     question = state.get("question", "")

#     print("ocr node active")
    
#     import PIL

#     image_path = state.get("image", "")

#     if not image_path:
#         print("DEBUG: No image path found in state.")
#         # Return early or handle the error appropriately
#         return {
#             "messages": ["Error: No image provided for OCR processing."],
#             "image": None 
#         }
    
#     image = PIL.Image.open(image_path)

#     prompt = """
#             Analyze the image of this medicine label. Extract the following information and return it as a clean JSON object.
#             Do not include any introductory text or markdown formatting like ```json.
            
#             The keys in the JSON should be:
#             - "medicine_name"
#             - "manufacturer"
#             - "active_salts" (as a list of strings)
#             - "expiry_date" (in DD-MM-YYYY format if possible, otherwise MM-YYYY)
            
#             If a piece of information is not available, set its value to null.
#         """
    
#     model = genai.GenerativeModel("gemini-2.5-flash")

#     response = model.generate_content([image, prompt])
#     extracted_text = response.text.strip()("```json", "").replace("```", "")

#     chain = image_ocr_prompt | groq_llm_with_tools
#     res = chain.ainvoke({
#         "extracted_text": extracted_text
#     })
#     print(f"ocr res: {res}")


VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
# Alternative if available: "meta-llama/llama-4-maverick-17b-128e-instruct" 

async def oc_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    OCR node: extract structured medicine label info using Groq vision model + optional refinement
    """
    print("ocr node active")
    question = state.get("question", "")
    image_path = state.get("image", "")
    # tool_result = state["messages"]

    # print(f"image -ath {image_path}")

    if not image_path or not isinstance(image_path, str):
        print("no image")
        # return {
        #     "messages": ["Error: No image provided for OCR processing."]
        # }

    try:
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image) 
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        buffered.seek(0)  
        base64_img = base64.b64encode(buffered.getvalue()).decode("utf-8")

        prompt = """
You are an expert at reading medicine labels (strips, bottles, cartons, blister packs — including Indian & international formats).
Analyze this image carefully and extract ONLY the requested fields.
Return **valid JSON only** — nothing else. No explanations, no markdown, no ```json, no extra text.

Rules:
- Missing / unclear / not visible → null
- "active_salts": list of strings, include strength/dosage if present e.g. ["Paracetamol 500 mg", "Ibuprofen 200 mg"]
- "expiry_date": prefer DD-MM-YYYY; if only month-year → "MM-YYYY"; if ambiguous → null
- Use exact spelling for medicine names & manufacturers
- Ignore MRP, batch no, manufacturing date unless part of name/salts

Output structure (JSON object):
{
  "medicine_name": string | null,
  "manufacturer": string | null,
  "active_salts": array of strings | null,
  "expiry_date": string | null
}
"""
        llm = ChatGroq(
            model=VISION_MODEL,
            temperature=0.0,          
            max_tokens=1024,
            # api_key=os.getenv("GROQ_API_KEY")  # usually from env
        )

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"},
                },
            ]
        )

        response: AIMessage = await llm.ainvoke([message])
        raw_text = response.content.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text[7:].strip()
        raw_text = raw_text.removesuffix("```").strip()

        # print(f"this is raw data: {raw_text}")

        try:
            extracted = json.loads(raw_text)
        except json.JSONDecodeError as e:
            print(f"error here {e}")
            # return {
            #     "messages": ["OCR failed — invalid JSON from vision model."],
            #     "ocr_result": {"error": "invalid_json", "raw": raw_text},
            #     "image": image_path
            # }
        chain = image_ocr_prompt | groq_llm_with_tools

        groq_input = {
            "extracted_text": json.dumps(extracted, ensure_ascii=False),
        }

        res = await chain.ainvoke(groq_input)

        # print(f"this is res {res}")

        return {
            "messages": [res]
        }

    except Exception as e:
        print(f"error {e}")
        # return {
        #     "messages": [f"OCR error: {str(e)}"],
        #     "ocr_result": None,
        #     "image": image_path
        # }


###################33333 ocr formatter ###########################

async def ocr_formatter(state: State) -> State:

    print("ocr formatter node active")

    question = state.get("question", "")
    summary = state.get("summary", "")
    tool_result = state["messages"][-1]

    # print(f"this is tool result :{tool_result}")

    chain = ocr_formatter_prompt | groq_llm
    res = await chain.ainvoke({
        "question": question,
        "summary": summary,
        "tool_result": tool_result
    })
    return {"messages": [res]}



######################### summarize conv ###################

async def sumarize_conv(state: State) -> State:

    print("summarize node active")

    summary = state.get("summary", "")
    messages = state.get("messages", "")

    transcript_parts = []

    if messages:
        for m in messages:
            content = getattr(m, "content", m)
            if isinstance(content, list):
                transcript_parts.append(" ".join(str(c) for c in content))
            else:
                transcript_parts.append(str(content))

    transcript_only = " ".join(part for part in transcript_parts if part)

    if summary:
        summary_msg = (
    f"Existing summary:\n{summary}\n\n"
    "Your task: Review the new conversation messages above and update the summary ONLY if there is genuinely new, changed, corrected, or additional important information.\n\n"

    "STRICT RULES:\n"
    "1. ALWAYS preserve critical factual details, especially:\n"
    "   - Names of hospitals, clinics, doctors, patients.\n"
    "   - Medicine names (brand/generic), dosage, frequency, duration.\n"
    "   - Test results, diagnoses, symptoms, allergies.\n"
    "   - Dates, times, locations, and instructions.\n"
    "   - Any numbers or medical measurements.\n"

    "2. NEVER remove, generalize, or replace proper nouns, medicine names, dosages, or other precise medical facts.\n"

    "3. If there is NO meaningful new information, RETURN THE EXISTING SUMMARY EXACTLY AS-IS.\n"

    "4. If updating is needed, keep the summary **as short and compact as possible while preserving ALL important facts**.\n"

    "5. Prefer concise bullet points when listing medicines, symptoms, or instructions.\n"

    "6. Do NOT add interpretations, assumptions, or external knowledge."
    )

    else:
        summary_msg = (
    "Create a concise summary of the conversation above.\n\n"

    "IMPORTANT: Preserve ALL critical medical facts, including:\n"
    "- Hospital, clinic, and doctor names\n"
    "- Medicine names (brand/generic), dosage, frequency, duration\n"
    "- Symptoms, diagnoses, allergies\n"
    "- Test results and medical measurements\n"
    "- Dates, locations, and instructions\n"

    "RULES:\n"
    "1. Do NOT remove or generalize proper nouns, medicine names, dosages, or numbers.\n"
    "2. Make the summary **as short as possible while keeping every important fact**.\n"
    "3. Use bullet points for lists (medicines, symptoms, instructions).\n"
    "4. Include only information explicitly stated in the conversation.\n"
    "5. Do NOT add assumptions or external information."
    )
        
    combined_msg = f"Conversation transcript: {transcript_only}\n\n {summary_msg}"

    messages = [
        HumanMessage(content=combined_msg)
    ]

    res = await groq_llm.ainvoke(messages)

    # print("this is res of sum", res)

    remaining_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary": res.content, "messages": remaining_messages}


################ memory ##################3

_pinecone_service : PineconeService | None = None
_embedding_service: LocalEmbeddingService | None = None
_pinecone_index = None


async def memory(state: State) -> State:
    global _embedding_service, _pinecone_service, _pinecone_index

    print("memory node active.")


    question = state.get("question")
    namespace = "user_12345"  # to remove

    if _embedding_service is None:
        # global _embedding_service
        _embedding_service = LocalEmbeddingService()
        # print("getting embedding service")
    # else:
        # print("embedding service already active")

    if _pinecone_service is None:
        # global _pinecone_service
        _pinecone_service = PineconeService()
        # print("getting pinecone service")
    # else:
        # print("pinecone service already active")


    if not question:
        pass # to handle later

    query_vector = _embedding_service.get_embedding(question)
    # print("converted to vector", query_vector[:5])

    if not _pinecone_index:
        # global _pinecone_index
        _pinecone_index = _pinecone_service.get_index()
        # print("getting pinecone index")
    # else:
    #     print("pinecone index already exists")

    pinecone_result = _pinecone_index.query(
        vector=query_vector,
        top_k=5,
        namespace=namespace,
        include_metadata=True
    )

    res_messages = []

    for match in pinecone_result["matches"]:
        meta = match["metadata"]

        text = meta.get("page_content", "")
        role = meta.get("role", "user")

        if role == "user":
            res_messages.append(HumanMessage(content=text))
        if role == "ai":
            res_messages.append(AIMessage(content=text))

    # print(f"this is result of memory: {res_messages}")

    return {"memory_docs": res_messages}

    
    
