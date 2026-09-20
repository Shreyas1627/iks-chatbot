import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="IKS <-> Engineering Chatbot", page_icon="🪔", layout="centered")

# --- API KEY CONFIGURATION ---
# In production (Streamlit Cloud), this fetches from Secrets. 
# Locally, you can set it in .streamlit/secrets.toml
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY. Please set it in Streamlit secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- SYSTEM PROMPT (The Core Engine) ---
# Designing a robust system prompt is the most critical part of this application. 
# It forces the model to strictly adhere to the bidirectional teaching requirement.
system_instruction = """
You are an expert professor specializing in the Indian Knowledge System (IKS) and Modern Engineering. 
Your goal is to bridge ancient Indian concepts (Sanskrit grammar, mathematics, astronomy) with modern engineering principles (computer science, civil, mechanical, etc.).

When teaching, you must dynamically apply one of these two approaches based on the user's query:
1. IKS to Engineering: If the user asks about an ancient concept (e.g., Panini's Astadhyayi, Pingala's Chhandashastra), explain the concept and immediately map it to its modern engineering equivalent (e.g., Backus-Naur Form, Compiler Design, Binary Combinatorics).
2. Engineering to IKS: If the user asks about a modern concept (e.g., Recursion, Hashing, State Machines), explain it simply and draw direct, historically accurate parallels to how ancient Indian scholars solved similar logical problems.

Rules:
- Always be historically and mathematically accurate.
- Use clear analogies.
- Format comparisons using Markdown tables where appropriate to show side-by-side relationships.
- Keep responses concise, structured, and engaging for an engineering student.
"""

# Initialize the Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=system_instruction
)

# --- SESSION STATE MANAGEMENT ---
# Initialize chat history so the bot remembers the context of the conversation
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- UI LAYOUT ---
st.title("🪔 IKS-Eng Connect")
st.markdown("**Bridge ancient Indian Knowledge Systems with Modern Engineering.**")

# Display suggestion chips for quick testing
st.markdown("_Try asking:_")
cols = st.columns(2)
with cols[0]:
    if st.button("Explain Compilers using Panini"):
        st.session_state.prompt_input = "How does Panini's Astadhyayi relate to modern Compiler Design?"
with cols[1]:
    if st.button("Explain Pingala's Binary System"):
        st.session_state.prompt_input = "Explain Pingala's Chhandashastra and its relation to binary code."

# Display chat history
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# --- CHAT INPUT & GENERATION ---
# Check if input came from a button or manual typing
user_input = st.chat_input("Ask a concept...")
if "prompt_input" in st.session_state:
    user_input = st.session_state.prompt_input
    del st.session_state.prompt_input # clear it

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and show assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # Stream the response for a better UX
        response = st.session_state.chat_session.send_message(user_input, stream=True)
        full_response = ""
        for chunk in response:
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)