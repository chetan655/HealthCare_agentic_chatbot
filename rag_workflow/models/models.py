from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq


from tools.tools import calculator
from schema.schema import ClassifierModelSchema


from dotenv import load_dotenv

load_dotenv()

tools = [calculator]
tool_node = ToolNode(tools)

llm = HuggingFaceEndpoint(
    repo_id='Qwen/Qwen3-VL-235B-A22B-Instruct'
)
refiner_model = ChatHuggingFace(
    llm=llm
)


# we are taking base model as gemini-2.0-flash

base_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash'
)

groq_llm = ChatGroq(
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

classifier_model = base_model.with_structured_output(ClassifierModelSchema)