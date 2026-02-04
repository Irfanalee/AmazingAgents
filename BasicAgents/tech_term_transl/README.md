# Technical Terminology Translator

A Streamlit app that translates complex technical, business, and academic terms into plain English using an AI agent.

## Features

- **Plain English explanations** - No jargon, just clear language
- **Four-part breakdown** for every term:
  - Plain English Definition
  - Worldly Analogy (relatable metaphor)
  - The Stakes (why you should care)
  - Memory Hook (one sentence to remember it)
- **Cost-efficient** - Uses gpt-4o-mini with session caching to minimize API calls
- **Internationalization support** - Handles OLI model and FDI terms

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key**

   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Example Terms to Try

- API, Blockchain, Machine Learning
- OLI Model, FDI, Agile Methodology
- Hedge Fund, Derivatives, Liquidity

## Tech Stack

- [Streamlit](https://streamlit.io/) - Web interface
- [Agno](https://github.com/agno-agi/agno) - AI agent framework
- [OpenAI](https://openai.com/) - GPT-4o-mini model
