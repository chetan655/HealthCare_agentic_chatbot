import streamlit as st
import requests
import uuid
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Healthcare AI",
    page_icon="🩺",
    layout="wide"
)

# BACKEND_URL = "https://healthcare-agentic-chatbot.onrender.com"
BACKEND_URL = "http://localhost:8000"

# -------------------------------
# Session State
# -------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "lat" not in st.session_state:
    st.session_state.lat = None

if "long" not in st.session_state:
    st.session_state.long = None


# -------------------------------
# Get Browser Location
# -------------------------------

components.html(
"""
<script>
navigator.geolocation.getCurrentPosition(function(position) {
    const lat = position.coords.latitude;
    const long = position.coords.longitude;

    const streamlitEvent = new CustomEvent("GET_LOCATION", {
        detail: {lat: lat, long: long}
    });

    window.parent.dispatchEvent(streamlitEvent);
});
</script>
""",
height=0
)

# Receive JS event
# loc = st.experimental_get_query_params()
loc = st.query_params

# -------------------------------
# Sidebar
# -------------------------------

with st.sidebar:
    st.title("⚙️ Settings")

    st.markdown("### 📍 Location")

    lat = st.text_input(
        "Latitude",
        value=st.session_state.lat or "29.9478"
    )

    long = st.text_input(
        "Longitude",
        value=st.session_state.long or "76.8170"
    )

    uploaded_file = st.file_uploader(
        "Upload Medical Image",
        type=["jpg","jpeg","png"]
    )


# -------------------------------
# Header
# -------------------------------

st.markdown(
"""
<h1 style='text-align:center; color:#2e86de'>
🩺 AI Healthcare Assistant
</h1>

<p style='text-align:center'>
Describe symptoms, upload reports, or find hospitals near you.
</p>
""",
unsafe_allow_html=True
)

# -------------------------------
# Chat History
# -------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -------------------------------
# Chat Input
# -------------------------------

if prompt := st.chat_input("Describe symptoms..."):

    st.session_state.messages.append(
        {"role":"user","content":prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

        if uploaded_file:
            st.image(uploaded_file, width=200)

    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_response = ""

        with st.spinner("Analyzing..."):

            try:

                form_data = {
                    "question": prompt,
                    "thread_id": st.session_state.thread_id,
                    "lat": lat,
                    "long": long
                }

                files = {}

                if uploaded_file:
                    uploaded_file.seek(0)

                    files = {
                        "image": (
                            uploaded_file.name,
                            uploaded_file,
                            uploaded_file.type
                        )
                    }

                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    data=form_data,
                    files=files,
                    stream=True,
                    timeout=120
                )

                if response.status_code == 200:

                    for chunk in response.iter_content():

                        if chunk:
                            token = chunk.decode("utf-8")

                            full_response += token

                            placeholder.markdown(
                                full_response + "▌"
                            )

                    placeholder.markdown(full_response)

                else:
                    full_response = f"Error {response.status_code}"

                    placeholder.markdown(full_response)

            except Exception as e:

                full_response = str(e)

                placeholder.markdown(full_response)

    st.session_state.messages.append(
        {"role":"assistant","content":full_response}
    )