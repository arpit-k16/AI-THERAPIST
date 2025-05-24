# =========================
# Imports & Configuration
# =========================
import streamlit as st
from datetime import datetime
from transformers import pipeline
import torch

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
# AI Model Setup (Free Alternative)
# =========================
@st.cache_resource
def load_model():
    """Load a free, local-running AI model"""
    return pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Free small model
        device="cpu",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )

# =========================
# Response Generation
# =========================
def generate_response(prompt):
    """Generate responses using the free local model"""
    memory = st.session_state.memory
    
    therapist_prompt = f"""You are a supportive listener talking to {memory['user_name'] or "someone"}.
    
Guidelines:
1. Tone: {memory['preferred_style']}
2. Sensitive topics: {memory['sensitive_topics']}
3. Be warm but professional
4. Keep responses under 3 sentences

Respond to:
"{prompt}" """

    try:
        generator = load_model()
        response = generator(
            therapist_prompt,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True
        )
        # Extract just the assistant's response
        return response[0]['generated_text'].split("\n")[-1].strip()
    except Exception as e:
        return "I'm having trouble responding. Could you rephrase that?"

# =========================
# UI Layout
# =========================
st.set_page_config(page_title="Supportive Listener", layout="centered")
st.title("Supportive Listener")
st.caption("A safe space to share your thoughts")

# =========================
# Sidebar Preferences
# =========================
with st.sidebar:
    st.subheader("Your Preferences")
    st.session_state.memory["user_name"] = st.text_input(
        "What should I call you?",
        st.session_state.memory["user_name"]
    )
    
    st.session_state.memory["preferred_style"] = st.selectbox(
        "Conversation style",
        ["gentle", "direct", "neutral"],
        index=["gentle", "direct", "neutral"].index(st.session_state.memory["preferred_style"])
    )
    
    st.session_state.memory["sensitive_topics"] = st.text_area(
        "Topics to handle carefully (optional)",
        "\n".join(st.session_state.memory["sensitive_topics"])
    ).split("\n")

# =========================
# Chat Display
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        st.caption(msg["time"])

# =========================
# Message Handling
# =========================
if prompt := st.chat_input("What's on your mind?"):
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": datetime.now().strftime("%H:%M")
    })
    
    # Generate and show response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            st.write(response)
    
    # Add assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "time": datetime.now().strftime("%H:%M")
    })

# =========================
# Conversation Management
# =========================
st.markdown("---")
if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()
