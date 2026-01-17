# Deep Research Assistant

A comprehensive research tool powered by OpenAI's API that conducts iterative web searches and generates detailed research reports.

## Features

- 🔍 **Interactive Research**: Answer clarifying questions to refine your research needs
- 🌐 **Web Search Integration**: Automated web searches using OpenAI's web search tool
- 📊 **Iterative Research**: Continues searching until research goal is satisfied
- 📄 **Comprehensive Reports**: Generates detailed reports with inline citations
- 🎨 **Streamlit UI**: User-friendly web interface

## Setup Instructions

### 1. Create Virtual Environment

**On macOS/Linux:**
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

**Or manually:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure API Key

You have two options:

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Option B: Streamlit Secrets**
Create a `.streamlit/secrets.toml` file:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
Deep Research/
├── app.py                    # Streamlit application
├── deep_research_clone.py    # Core research functions (modular)
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── setup_venv.sh            # Virtual environment setup script
└── README.md                # This file
```

## How It Works

### Step-by-Step Process:

1. **Topic Input**: User enters research topic
2. **Question Generation**: System generates 5 clarifying questions
3. **User Answers**: User answers questions to refine research scope
4. **Goal & Queries**: System creates research goal and initial search queries
5. **Iterative Research**: 
   - Executes web searches
   - Evaluates if research is complete
   - Generates additional queries if needed
   - Repeats until goal is satisfied
6. **Report Generation**: Creates comprehensive report with citations

## Code Modules

### `deep_research_clone.py`

Modular functions organized by purpose:

- **Configuration Module**: Setup and constants
- **Question Generation Module**: Creates clarifying questions
- **Goal and Query Generation Module**: Generates research plan
- **Web Search Module**: Executes web searches
- **Evaluation Module**: Assesses research completeness
- **Research Execution Module**: Orchestrates iterative research
- **Report Generation Module**: Creates final report

### `app.py`

Streamlit interface with:
- Multi-step wizard interface
- Progress indicators
- Session state management
- Error handling
- Report download functionality

## Requirements

- Python 3.8+
- OpenAI API key
- openai==1.78.1
- streamlit>=1.28.0

## Notes

- The code uses OpenAI's `responses.create()` API endpoint
- Models used: `gpt-4.1` and `gpt-4.1-mini`
- Web search tool is enabled for research queries

## License

This project is for research and educational purposes.
