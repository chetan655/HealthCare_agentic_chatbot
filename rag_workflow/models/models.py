from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from schema.schema import ClassifierModelSchema


from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id='Qwen/Qwen3-VL-235B-A22B-Instruct'
)
# refiner_model = ChatHuggingFace(
#     llm=llm
# )


# we are taking base model as gemini-2.0-flash

base_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash'
)


chat_node_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash'
)

refiner_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
    disable_streaming=True,
    verbose=False,
    callbacks=[]
)

classifier_model = base_model.with_structured_output(ClassifierModelSchema)