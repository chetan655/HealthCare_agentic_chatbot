import streamlit as st
import requests

# --- Page setup ---
st.set_page_config(page_title="Healthcare Chatbot (Under Development)", page_icon="💬", layout="centered")

# --- Title & Subheader ---
st.title("🩺 Healthcare Agentic Chatbot")
st.caption("🚧 This chatbot is currently under development. Responses may be experimental.")

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display previous messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User input ---
if prompt := st.chat_input("Type your message..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Prepare assistant message container ---
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # --- Spinner during backend response ---
        with st.spinner("💭 Thinking..."):
            try:
                # --- Stream tokens from backend ---
                with requests.post(
                    "https://healthcare-agentic-chatbot.onrender.com/chat",
                    json={"query": prompt},
                    stream=True,     # <-- enable streaming
                    timeout=120
                ) as response:
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=None):
                            if chunk:
                                token = chunk.decode("utf-8")
                                full_response += token
                                message_placeholder.markdown(full_response + "▌")
                    else:
                        full_response = f"⚠️ Error {response.status_code}: Failed to get response from server."
            except Exception as e:
                full_response = f"❌ Server connection error: {str(e)}"

        # --- Remove cursor and finalize text ---
        message_placeholder.markdown(full_response)
    
    # --- Add assistant message to history ---
    st.session_state.messages.append({"role": "assistant", "content": full_response})
