# Warren - M&A Valuation Expert

Warren is your Claude-powered M&A valuation expert coding partner. Ask him questions about company valuation, deal structuring, financial modeling, and M&A strategy.

## Setup

### 1. Install Dependencies
```bash
pip install anthropic
```

### 2. Set Your API Key
Make sure you have your Anthropic API key set:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage

### From Terminal
```bash
# Direct usage with Python
python3 warren.py "Your question about M&A valuation"

# Or using the shell wrapper
./warren "Your question about M&A valuation"
```

### Examples
```bash
./warren "What are the key steps in a DCF analysis?"

./warren "How do I value a SaaS company for acquisition?"

./warren "What multiples should I use for tech company comparables?"

./warren "What are the tax implications of different deal structures?"
```

### In VS Code
You can integrate Warren into VS Code by:

1. **Adding to PATH** (optional, for global access):
   ```bash
   export PATH="/Users/irfan/Documents/AI_Projects/CorpVal:$PATH"
   ```

2. **Running in VS Code Terminal**:
   Press `Ctrl+`` (backtick) to open the integrated terminal and run:
   ```bash
   ./warren "What is EBITDA multiples for healthcare companies?"
   ```

3. **Creating a VS Code Keybinding** (optional):
   Edit `.vscode/keybindings.json`:
   ```json
   {
     "key": "ctrl+shift+w",
     "command": "workbench.action.terminal.sendSequence",
     "args": {"text": "# Ask Warren about M&A valuation\n"}
   }
   ```

## Warren's Expertise

Warren can help you with:
- **Valuation Methods**: DCF, Comparables, Precedent Transactions, Asset-Based
- **Financial Modeling**: Projections, sensitivity analysis, scenarios
- **M&A Process**: Deal structure, tax, regulatory, due diligence
- **Industry Knowledge**: Multiples, benchmarking, competitive analysis

## Example Questions

- "What's the difference between EV/EBITDA and EV/Revenue multiples?"
- "How do I build a 5-year financial projection for a manufacturing company?"
- "What due diligence items are most important for a tech acquisition?"
- "How do I calculate the cost of equity for a DCF model?"
- "What's a typical earnout structure in M&A deals?"

## Architecture

- `warren.py`: Main Python script that interfaces with Claude API
- `warren`: Shell wrapper for easy command-line access
- System prompt defines Warren's expertise and communication style
