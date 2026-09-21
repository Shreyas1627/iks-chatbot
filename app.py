import time
import streamlit as st
from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IKS ↔ Engineering Chatbot",
    page_icon="🪔",
    layout="centered"
)


# ============================================================
# API KEY
# ============================================================

if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "Missing GEMINI_API_KEY. "
        "Please add it to Streamlit Secrets."
    )
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are an expert professor specializing in the Indian Knowledge
System (IKS) and Modern Engineering.

Your goal is to bridge ancient Indian concepts such as Sanskrit
grammar, mathematics, astronomy, logic, linguistics and philosophy
with modern engineering principles such as computer science,
software engineering, civil engineering, mechanical engineering,
mathematics and information theory.

When teaching, dynamically use one of these approaches:

1. IKS → Engineering

If the user asks about an ancient concept, for example:
- Panini's Astadhyayi
- Pingala's Chhandashastra
- Indian mathematics
- ancient Indian astronomy
- Sanskrit grammatical rules

Explain the historical concept first and then carefully map it
to relevant modern engineering concepts.

Examples:
- Panini → formal grammar / compiler concepts
- Pingala → combinatorics / binary-like representations
- ancient algorithms → algorithmic thinking

Do NOT claim that an ancient system is literally identical to a
modern technology. Clearly distinguish historical facts from
modern analogies.

2. Engineering → IKS

If the user asks about a modern engineering concept, for example:
- recursion
- hashing
- state machines
- algorithms
- databases
- compiler design
- networks
- artificial intelligence

Explain the modern concept clearly and then identify relevant
parallels or conceptual connections in Indian intellectual
traditions where historically justified.

IMPORTANT RULES:

- Be historically accurate.
- Do not invent historical evidence.
- Clearly distinguish historical evidence from modern analogy.
- Be mathematically accurate.
- Do not exaggerate ancient achievements.
- If a claimed connection is uncertain or debated, say so.
- Use simple explanations suitable for an engineering student.
- Use examples whenever helpful.
- Use Markdown headings and tables when they improve clarity.
- Keep answers reasonably concise and structured.
"""


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-3.8-flash"

GENERATION_CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    temperature=0.7,
    max_output_tokens=1000,
)


# ============================================================
# SESSION STATE
# ============================================================

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL_NAME,
        config=GENERATION_CONFIG,
    )

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# HELPER FUNCTION
# ============================================================

def send_message_with_retry(message, max_retries=3):
    """
    Send a message to Gemini with exponential backoff.

    This helps with temporary RESOURCE_EXHAUSTED / rate-limit
    errors, but it cannot fix a completely exhausted daily quota.
    """

    for attempt in range(max_retries):
        try:
            return st.session_state.chat.send_message_stream(
                message=message
            )

        except Exception as e:

            error_text = str(e).lower()

            if (
                "resourceexhausted" in error_text
                or "429" in error_text
                or "quota" in error_text
                or "rate limit" in error_text
            ):

                if attempt == max_retries - 1:
                    raise

                wait_time = 2 ** attempt
                time.sleep(wait_time)

            else:
                raise


# ============================================================
# UI
# ============================================================

st.title("🪔 IKS-Eng Connect")

st.markdown(
    "**Bridge ancient Indian Knowledge Systems "
    "with Modern Engineering.**"
)


# ============================================================
# QUICK QUESTIONS
# ============================================================

st.markdown("### Try asking")

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "📚 Panini → Compilers",
        use_container_width=True
    ):
        st.session_state.prompt_input = (
            "How does Panini's Astadhyayi relate "
            "to modern compiler design?"
        )

with col2:
    if st.button(
        "🔢 Pingala → Binary",
        use_container_width=True
    ):
        st.session_state.prompt_input = (
            "Explain Pingala's Chhandashastra "
            "and its relationship to combinatorics "
            "and binary representations."
        )


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask about IKS, engineering, or their connections..."
)


# Handle quick-question buttons
if "prompt_input" in st.session_state:

    user_input = st.session_state.prompt_input

    del st.session_state.prompt_input


# ============================================================
# GENERATE RESPONSE
# ============================================================

if user_input:

    # Save and display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)


    # Generate assistant response
    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        full_response = ""

        try:

            stream = send_message_with_retry(user_input)

            for chunk in stream:

                if chunk.text:

                    full_response += chunk.text

                    message_placeholder.markdown(
                        full_response + "▌"
                    )

            message_placeholder.markdown(full_response)


            # Save assistant response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )


        except Exception as e:

            error_text = str(e).lower()

            if (
                "resourceexhausted" in error_text
                or "429" in error_text
                or "quota" in error_text
            ):

                message_placeholder.error(
                    "⚠️ Gemini API quota/rate limit reached.\n\n"
                    "Please wait and try again, or check your "
                    "Gemini API quota in Google AI Studio."
                )

            else:

                message_placeholder.error(
                    "❌ Something went wrong while contacting Gemini."
                )

                st.exception(e)
