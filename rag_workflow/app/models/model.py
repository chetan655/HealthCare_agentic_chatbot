from app.schema.schema import ClassifierModelSchema

from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

from app.tools.tools import search ,find_nearby_hospitals

from dotenv import load_dotenv

load_dotenv()

############### tools #########################
tools = [search, find_nearby_hospitals]
tool_node = ToolNode(tools)

# flash_2_5 = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash"
# )

groq_llm = ChatGroq(
    # model = "openai/gpt-oss-20b"
    model = "llama-3.3-70b-versatile"
)

groq_llm_with_tools = groq_llm.bind_tools(tools)

classifier_model = groq_llm.with_structured_output(ClassifierModelSchema)