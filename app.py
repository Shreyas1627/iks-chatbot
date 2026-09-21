import streamlit as st
from openai import OpenAI


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IKS ↔ Engineering Chatbot",
    page_icon="🪔",
    layout="centered"
)


# ============================================================
# API KEY CONFIGURATION
# ============================================================

if "XAI_API_KEY" not in st.secrets:
    st.error(
        "Missing XAI_API_KEY. "
        "Please add it to Streamlit Secrets."
    )
    st.stop()

client = OpenAI(
    api_key=st.secrets["XAI_API_KEY"],
    base_url="https://api.x.ai/v1"
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

system_instruction = """
You are an expert professor specializing in the Indian Knowledge
System (IKS) and Modern Engineering.

Your goal is to bridge ancient Indian concepts such as Sanskrit
grammar, mathematics, astronomy, logic and linguistics with
modern engineering principles such as computer science, software
engineering, civil engineering, mechanical engineering and
information theory.

When teaching, dynamically use one of these approaches:

1. IKS → Engineering

If the user asks about an ancient concept such as:
- Panini's Astadhyayi
- Pingala's Chhandashastra
- Indian mathematics
- ancient Indian astronomy
- Sanskrit grammar

Explain the historical concept first and then carefully map it
to relevant modern engineering concepts.

Examples:
- Panini → formal grammar / compiler concepts
- Pingala → combinatorics / binary representations
- ancient algorithms → algorithmic thinking

Do NOT claim that an ancient system is literally identical to
a modern technology. Clearly distinguish historical facts from
modern analogies.

2. Engineering → IKS

If the user asks about a modern engineering concept such as:
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
- If a connection is uncertain or debated, say so.
- Use simple explanations suitable for an engineering student.
- Use examples whenever helpful.
- Use Markdown headings and tables when they improve clarity.
- Keep answers reasonably concise and structured.
"""


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "grok-4.6"


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


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
# DISPLAY CHAT HISTORY
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


# Handle quick buttons
if "prompt_input" in st.session_state:

    user_input = st.session_state.prompt_input

    del st.session_state.prompt_input


# ============================================================
# SEND MESSAGE
# ============================================================

if user_input:

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)


    # --------------------------------------------------------
    # Build conversation
    # --------------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": system_instruction
        }
    ]

    messages.extend(st.session_state.messages)


    # --------------------------------------------------------
    # Generate response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        full_response = ""

        try:

            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                stream=True,
            )

            for chunk in stream:

                if chunk.choices:

                    delta = chunk.choices[0].delta

                    if delta.content:

                        full_response += delta.content

                        message_placeholder.markdown(
                            full_response + "▌"
                        )

            message_placeholder.markdown(
                full_response
            )


            # Save assistant response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )


        except Exception as e:

            error_message = str(e)

            if "429" in error_message:

                message_placeholder.error(
                    "⚠️ Grok API rate limit or quota reached. "
                    "Please wait and try again."
                )

            else:

                message_placeholder.error(
                    "❌ Error communicating with Grok."
                )

                st.exception(e)
