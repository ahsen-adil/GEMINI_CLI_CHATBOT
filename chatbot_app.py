
import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- Configuration ---
# Use secrets for production environments
# For this example, the API key is hardcoded as requested.
API_KEY = "AIzaSyAMWmWhxjmoPKrOXTWPFaZ5BR_m9F487FY"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}")
    st.stop()

# --- Page Setup ---
st.set_page_config(page_title="AI Chatbot – Powered by Gemini Cli", page_icon="🤖")
st.title("AI Chatbot – Powered by Gemini Cli")

# --- Styling for Message Bubbles ---
st.markdown("""
<style>
.st-emotion-cache-1f833ft, .st-emotion-cache-4oygw6, .st-emotion-cache-16txtl3 {
    color: black;
}
.chat-row {
    display: flex;
    margin-bottom: 10px;
}
.user-row {
    justify-content: flex-end;
}
.bot-row {
    justify-content: flex-start;
}
.chat-bubble {
    padding: 12px 18px;
    border-radius: 18px;
    max-width: 75%;
    word-wrap: break-word;
    color: #333; /* Explicitly set a dark text color */
}
.user-bubble {
    background-color: #DCF8C6;
    text-align: right;
}
.bot-bubble {
    background-color: #F1F0F0;
    text-align: left;
}
.chat-meta {
    font-size: 0.7em;
    color: #666;
    text-align: right;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("Controls")
    personality = st.selectbox(
        "Choose Bot Personality:",
        ("Friendly", "Professional", "Sarcastic", "Motivational")
    )
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# --- System Prompt Definition ---
system_prompt = f"You are an AI assistant with a {personality.lower()} personality. Respond clearly and briefly."

# --- Display Chat History ---
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        timestamp = message["timestamp"]

        row_class = "user-row" if role == "You" else "bot-row"
        bubble_class = "user-bubble" if role == "You" else "bot-bubble"
        
        st.markdown(
            f'<div class="chat-row {row_class}">'
            f'  <div class="chat-bubble {bubble_class}">'
            f'    <b>{role}:</b> {content}'
            f'    <div class="chat-meta">{timestamp.strftime("%Y-%m-%d %H:%M:%S")}</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True
        )


# --- Chat Input Form ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message:", key="user_input", placeholder="Type your message here...")
    send_button = st.form_submit_button("Send")

# --- Handle User Input and Generate Response ---
if send_button and user_input:
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "You",
        "content": user_input,
        "timestamp": datetime.now()
    })

    # Prepare context for the model
    # We send the system prompt and the last few messages for context
    conversation_context = [system_prompt]
    for msg in st.session_state.chat_history[-5:]: # Send last 5 messages for context
        conversation_context.append(f'{msg["role"]}: {msg["content"]}')
    
    full_prompt = "\n".join(conversation_context)

    # Generate response from Gemini
    try:
        with st.spinner("Bot is thinking..."):
            response = model.generate_content(full_prompt)
            bot_reply = response.text

        # Add bot response to history
        st.session_state.chat_history.append({
            "role": "Bot",
            "content": bot_reply,
            "timestamp": datetime.now()
        })
        st.rerun()

    except Exception as e:
        st.error(f"An error occurred while generating the response: {e}")

# To run the app:
# 1. Make sure you have the required libraries: pip install streamlit google-generativeai
# 2. Save the code as chatbot_app.py
# 3. Run `streamlit run chatbot_app.py` in your terminal.
