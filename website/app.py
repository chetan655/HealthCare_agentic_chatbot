import streamlit as st
import requests
import uuid

# --- Page setup ---
st.set_page_config(page_title="Healthcare Chatbot", page_icon="🩺", layout="wide")

# --- Constants ---
# BACKEND_URL = "https://healthcare-agentic-chatbot.onrender.com"  # Update if running locally (e.g., http://127.0.0.1:8000)
BACKEND_URL = "https://healthcare-agentic-chatbot.onrender.com/"  # Update if running locally (e.g., http://127.0.0.1:8000)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# --- Sidebar: Location & Tools ---
with st.sidebar:
    st.header("⚙️ Settings & Tools")
    
    st.subheader("📍 Location Context")
    # Defaulting to Gurugram coordinates for demo purposes
    lat = st.number_input("Latitude", value=28.4595, format="%.4f")
    long = st.number_input("Longitude", value=77.0266, format="%.4f")
    
    st.markdown("---")
    
    st.subheader("📸 Image Upload")
    uploaded_file = st.file_uploader("Upload Medical Report/Image", type=["jpg", "jpeg", "png"])
    
    st.markdown("---")
    
    # --- SOS BUTTON ---
    # st.subheader("🚨 Emergency")
    # if st.button("TRIGGER SOS", type="primary", use_container_width=True):
    #     with st.spinner("Broadcasting Emergency Alert..."):
    #         try:
    #             # The SOS endpoint expects JSON body
    #             sos_payload = {
    #                 "latitude": lat,
    #                 "longitude": long
    #             }
    #             sos_response = requests.post(f"{BACKEND_URL}/sos", json=sos_payload)
    #             if sos_response.status_code == 200:
    #                 st.success("SOS Sent to Emergency Contacts!")
    #             else:
    #                 st.error(f"Failed to send SOS: {sos_response.text}")
    #         except Exception as e:
    #             st.error(f"Connection Error: {e}")

# --- Main Interface ---
st.title("🩺 Healthcare Agentic Chatbot")
st.caption("Context-aware medical assistant with vision & emergency capabilities.")

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Describe your symptoms or ask a question..."):
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_file:
            st.image(uploaded_file, caption="Attached Image", width=200)

    # 2. Prepare Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        with st.spinner("Analyzing..."):
            try:
                # --- Prepare Data for Multipart/Form-Data Request ---
                # Text fields must be strings
                form_data = {
                    "question": prompt,
                    "thread_id": st.session_state.thread_id,
                    "lat": str(lat),
                    "long": str(long)
                }
                
                # File payload
                files = {}
                if uploaded_file:
                    # Reset pointer to ensure file is read correctly
                    uploaded_file.seek(0)
                    files = {"image": (uploaded_file.name, uploaded_file, uploaded_file.type)}

                # --- Stream Request ---
                with requests.post(
                    f"{BACKEND_URL}/chat",
                    data=form_data,   # Use 'data' for form fields
                    files=files,      # Use 'files' for uploads
                    stream=True,
                    timeout=120
                ) as response:
                    
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=None):
                            if chunk:
                                token = chunk.decode("utf-8")
                                full_response += token
                                message_placeholder.markdown(full_response + "▌")
                        
                        # Final render without cursor
                        message_placeholder.markdown(full_response)
                    else:
                        error_msg = f"⚠️ Error {response.status_code}: {response.text}"
                        message_placeholder.markdown(error_msg)
                        full_response = error_msg
                        
            except Exception as e:
                error_msg = f"❌ Server connection error: {str(e)}"
                message_placeholder.markdown(error_msg)
                full_response = error_msg

    # 3. Save Assistant Message
    st.session_state.messages.append({"role": "assistant", "content": full_response})