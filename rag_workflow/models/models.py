from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq


from tools.tools import calculator, search, find_nearby_hospitals, medicine_ocr_tool, medicine_database_lookup_tool
from schema.schema import ClassifierModelSchema



from dotenv import load_dotenv

load_dotenv()

tools = [calculator, search, find_nearby_hospitals, medicine_database_lookup_tool]
tool_node = ToolNode(tools)

llm = HuggingFaceEndpoint(
    repo_id='openai/gpt-oss-120b'
)
refiner_model = ChatHuggingFace(
    llm=llm
)

# summarizer_llm = HuggingFaceEndpoint(
#     # repo_id='openai/gpt-oss-120b'
#     repo_id='Qwen/Qwen3-Next-80B-A3B-Instruct'
# )
# summary_model = ChatHuggingFace(llm=summarizer_llm)


# we are taking base model as gemini-2.0-flash

# summary_model = ChatGoogleGenerativeAI(
#     model='gemini-2.0-flash'
# )

base_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash'
)

groq_llm = ChatGroq(
    model='openai/gpt-oss-120b'
)

summary_model = ChatGroq(
    model='openai/gpt-oss-120b'
)

groq_llm_for_general_with_tools = groq_llm.bind_tools(tools)

base_model_with_tools = base_model.bind_tools(tools)

# chat_node_model = ChatGoogleGenerativeAI(
#     model='gemini-2.0-flash'
# )

# refiner_model = ChatGoogleGenerativeAI(
#     model='gemini-2.0-flash',
# )
# refiner_model = 

# base_model1 = ChatGoogleGenerativeAI(
#     model='gemini-2.-flash-lite'
# )

classifier_model = groq_llm.with_structured_output(ClassifierModelSchema)