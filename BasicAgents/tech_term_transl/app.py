"""
Technical Terminology Translator
A Streamlit app that uses an Agno Agent to explain technical terms in plain English.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Technical Terminology Translator",
    page_icon="📚",
    layout="centered"
)

# System instructions that define how the agent should respond
translator_instructions = """
You are a Technical Terminology Translator. Your job is to explain complex technical,
business, and academic terms so that anyone can understand them.

Writing Style Rules:
- Use active voice exclusively
- Avoid buzzwords and corporate jargon
- Maintain a calm, confident tone
- Be direct and clear

For every term you explain, you must provide exactly four sections:

## Plain English Definition
Explain what the term means without using any technical jargon. Write as if explaining
to a smart friend who works in a completely different field.

## The Worldly Analogy
Create a relatable metaphor from everyday life. Use examples from cooking, sports,
relationships, nature, or other universal experiences. The analogy should make the
concept click instantly.

## The Stakes
Explain why a non-technical person should care about this term. How does it affect
their daily life, their job, their money, or their decisions? Be specific and practical.

## Memory Hook
Write one short, punchy sentence that captures the essence of the term. This should
be memorable enough that they can recall it weeks later.

Special Context - Internationalization Terms:
If someone asks about the OLI model (Ownership, Location, Internalization) or related
international business concepts like FDI, multinational enterprises, or market entry
strategies, provide the same four sections with examples relevant to global business
decisions and how companies choose where and how to operate internationally.

Always format your response with clear markdown headers for each section.
"""


@st.cache_resource
def create_translator_agent():
    """
    Create and return the Agno agent configured for terminology translation.
    Cached to avoid recreating the agent on every Streamlit rerun - saves resources.
    """
    agent = Agent(
        # gpt-4o-mini is cost-efficient: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=translator_instructions,
        markdown=True
    )
    return agent


def get_cached_translation(term):
    """Check if we already translated this term in the current session."""
    if "translation_cache" not in st.session_state:
        st.session_state.translation_cache = {}
    return st.session_state.translation_cache.get(term.lower().strip())


def save_to_cache(term, translation):
    """Save translation to session cache to avoid duplicate API calls."""
    if "translation_cache" not in st.session_state:
        st.session_state.translation_cache = {}
    st.session_state.translation_cache[term.lower().strip()] = translation


def translate_term(agent, technical_term):
    """
    Send a term to the agent and get the plain English explanation.
    Uses session cache to avoid redundant API calls for the same term.
    """
    # Check cache first to save API costs
    cached_result = get_cached_translation(technical_term)
    if cached_result:
        return cached_result, True  # Return cached result with flag

    prompt = f"Explain the following term: {technical_term}"
    response = agent.run(prompt)
    translation = response.content

    # Save to cache for future use
    save_to_cache(technical_term, translation)
    return translation, False  # Return fresh result with flag


def main():
    """Main function that runs the Streamlit app."""

    # App header
    st.title("Technical Terminology Translator")
    st.markdown(
        "Enter any technical, business, or academic term and get a clear, "
        "jargon-free explanation that anyone can understand."
    )

    # Create a divider for visual separation
    st.divider()

    # Input section
    term_to_translate = st.text_input(
        label="Enter a technical term",
        placeholder="e.g., API, Blockchain, OLI Model, Machine Learning, Agile...",
        help="Type any term you want explained in plain English"
    )

    translate_button = st.button("Translate", type="primary", use_container_width=True)

    # Process the request when button is clicked
    if translate_button and term_to_translate:
        # Check if we have a cached result first
        cached_result = get_cached_translation(term_to_translate)

        if cached_result:
            # Use cached result - no API call needed
            explanation = cached_result
            was_cached = True
        else:
            # Show a spinner while making API call
            with st.spinner(f"Translating '{term_to_translate}'..."):
                # Get the cached agent (only created once per session)
                translator_agent = create_translator_agent()

                # Get the translation
                explanation, was_cached = translate_term(translator_agent, term_to_translate)

        # Display section
        st.divider()
        st.subheader(f"Translation: {term_to_translate}")

        # Show cache status to user
        if was_cached:
            st.caption("📦 Retrieved from cache (no API call)")

        # Show the agent's response in a clean container
        st.markdown(explanation)

    elif translate_button and not term_to_translate:
        # Handle empty input
        st.warning("Please enter a term to translate.")

    # Footer with examples
    st.divider()
    with st.expander("Example terms you can try"):
        st.markdown("""
        **Technology:**
        - API (Application Programming Interface)
        - Blockchain
        - Machine Learning
        - Cloud Computing

        **Business:**
        - OLI Model (Ownership, Location, Internalization)
        - FDI (Foreign Direct Investment)
        - Agile Methodology
        - KPI (Key Performance Indicator)

        **Finance:**
        - Hedge Fund
        - Derivatives
        - Liquidity
        - Amortization
        """)


if __name__ == "__main__":
    main()
