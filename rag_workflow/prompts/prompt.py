from langchain_core.prompts import ChatPromptTemplate

refiner_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a medical query refiner. "
               "Rewrite the user’s input into a clear, unambiguous question. "
               "Expand abbreviations, fix grammar, and remove vagueness. "
               "Do not answer the question, only refine it."),
    ("user", "{question}")
])