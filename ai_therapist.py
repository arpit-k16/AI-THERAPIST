# =========================
# Imports & Configuration
# =========================
import streamlit as st
import ollama
from datetime import datetime

# =========================
# Session State Management
# =========================
if "memory" not in st.session_state:
    st.session_state.memory = {
        "user_name": "",
        "sensitive_topics": [],
        "preferred_style": "gentle"
    }

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello, I'm here to listen. How are you feeling today?",
        "time": datetime.now().strftime("%H:%M")
    })

# =========================
# Utility Functions
# =========================
def generate_response(prompt):
    """Generate a friendly, supportive response using the current session memory."""
    memory = st.session_state.memory

    therapist_prompt = f"""You are a friendly, supportive assistant chatting with {memory['user_name'] or "the user"}.

Guidelines:
1. Keep a warm, approachable, and respectful tone.
2. Show empathy and understanding, but don't be overly familiar or intrusive.
3. Use the user's preferred name or form of address.
4. Focus on listening, encouragement, and gentle reflection.
5. Be mindful of sensitive topics: {memory['sensitive_topics']}
6. Response style: {memory['preferred_style']}

Example responses:
- "Thanks for sharing that. Want to talk a bit more about it?"
- "That sounds tough. How have you been coping?"
- "I'm here for you—feel free to say whatever's on your mind."

Respond to:
"{prompt}" """

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": therapist_prompt},
            {"role": "user", "content": prompt}
        ],
        options={'temperature': 0.5}
    )
    return response['message']['content']

# =========================
# UI Layout & Page Config
# =========================
st.set_page_config(page_title="Professional Listener", layout="centered")
st.title("Emotional Support Chat")
st.caption("A relaxed, safe space to talk things through.")

# (No custom CSS. Streamlit's default styling is used.)

# =========================
# Sidebar: User Preferences
# =========================
with st.sidebar:
    st.subheader("Your Preferences")
    st.session_state.memory["user_name"] = st.text_input(
        "What should I call you?",
        st.session_state.memory["user_name"]
    )

    st.session_state.memory["preferred_style"] = st.selectbox(
        "Chat style",
        ["gentle", "direct", "neutral"],
        index=["gentle", "direct", "neutral"].index(st.session_state.memory["preferred_style"])
    )

    st.session_state.memory["sensitive_topics"] = st.text_area(
        "Anything you'd like me to be extra careful about? (optional)",
        "\n".join(st.session_state.memory["sensitive_topics"])
    ).split("\n")

    st.markdown("---")
    st.caption("These help me make our chat more comfortable for you.")

# =========================
# Main Chat Display
# =========================
st.markdown("### Our Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Always display the message content, even if it's empty
        st.write(msg["content"])
        st.caption(msg["time"])

# =========================
# Chat Input & Response Handling
# =========================
prompt = st.chat_input("What's on your mind?")

if prompt is not None:
    if prompt.strip():
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "time": datetime.now().strftime("%H:%M")
        })
        # Rerun immediately to show the user's message in the UI before generating a response
        st.rerun()

# After rerun, check if the last message is from the user and not yet responded to
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Listening carefully..."):
            response = generate_response(st.session_state.messages[-1]["content"])
            st.write(response)
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "time": datetime.now().strftime("%H:%M")
    })
    st.rerun()

# =========================
# Actions
# =========================
st.markdown("---")
if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()