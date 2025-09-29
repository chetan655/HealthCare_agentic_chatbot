from langchain_google_genai import ChatGoogleGenerativeAI


chat_node_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash'
)

refiner_model = None