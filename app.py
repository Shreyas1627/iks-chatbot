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
# OPENAI API CONFIGURATION
# ============================================================

if "OPENAI_API_KEY" not in st.secrets:
    st.error(
        "Missing OPENAI_API_KEY. "
        "Please add it to your Streamlit Secrets."
    )
    st.stop()

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gpt-5.6-luna"


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are an expert professor specializing in the Indian Knowledge
System (IKS) and Modern Engineering.

Your goal is to bridge ancient Indian concepts such as:

- Sanskrit grammar
- Mathematics
- Astronomy
- Logic
- Linguistics
- Algorithms
- Indian scientific traditions

with modern engineering disciplines such as:

- Computer Science
- Software Engineering
- Artificial Intelligence
- Information Theory
- Civil Engineering
- Mechanical Engineering
- Mathematics

IMPORTANT TEACHING APPROACH:

1. IKS → Engineering

When the user asks about an ancient Indian concept:

First explain the historical concept clearly.

Then identify relevant modern engineering concepts.

For example:

Panini's grammar
→ Formal grammars
→ Parsing
→ Compiler design

Pingala's Chhandashastra
→ Combinatorics
→ Binary-like representation
→ Algorithmic thinking

However, DO NOT claim that an ancient system is literally
the same as a modern technology.

Clearly distinguish:

- Historical fact
- Modern interpretation
- Analogy
- Speculation

2. Engineering → IKS

When the user asks about a modern engineering concept:

First explain the modern engineering concept clearly.

Then discuss relevant parallels from Indian intellectual
traditions when there is legitimate historical evidence.

Examples:

Recursion
→ Recursive mathematical or grammatical structures

Formal grammar
→ Paninian grammatical rules

Combinatorics
→ Pingala's prosodic analysis

IMPORTANT RULES:

- Be historically accurate.
- Do not invent historical evidence.
- Do not exaggerate ancient Indian achievements.
- Do not present modern interpretations as historical facts.
- If a connection is debated, explicitly say so.
- Be mathematically accurate.
- Use simple explanations suitable for engineering students.
- Use examples whenever useful.
- Use Markdown headings.
- Use Markdown tables for useful comparisons.
- Keep answers concise but informative.
- Encourage curiosity and critical thinking.
"""


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# HEADER
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

        st.markdown(
            message["content"]
        )


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

    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(user_input)


    # --------------------------------------------------------
    # Prepare conversation
    # --------------------------------------------------------

    input_messages = [
        {
            "role": "developer",
            "content": SYSTEM_INSTRUCTION
        }
    ]

    input_messages.extend(
        st.session_state.messages
    )


    # --------------------------------------------------------
    # Generate response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        full_response = ""

        try:

            stream = client.responses.create(
                model=MODEL_NAME,
                input=input_messages,
                stream=True,
            )

            for event in stream:

                if event.type == "response.output_text.delta":

                    full_response += event.delta

                    message_placeholder.markdown(
                        full_response + "▌"
                    )


            # Final response
            message_placeholder.markdown(
                full_response
            )


            # ------------------------------------------------
            # Save assistant message
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )


        except Exception as e:

            error_message = str(e)

            if (
                "429" in error_message
                or "rate limit" in error_message.lower()
                or "quota" in error_message.lower()
            ):

                message_placeholder.error(
                    "⚠️ OpenAI API rate limit or quota reached. "
                    "Please wait and try again."
                )

            elif "401" in error_message:

                message_placeholder.error(
                    "🔑 Invalid OpenAI API key. "
                    "Check your Streamlit Secrets."
                )

            else:

                message_placeholder.error(
                    "❌ Error communicating with OpenAI."
                )

                st.exception(e)
