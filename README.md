# Proofreader

A lightweight, high-performance structured text proofreading utility. It leverages a structured LLM API on Replicate to analyze your text and provide grammatical corrections, stylistic rewrites, and detailed explanation metrics through a modern, responsive web dashboard.

Vibe-coded with Antigravity 2.0 and Gemini-3.5-Flash (Medium)

---

## Key Features

- **Interactive Web Interface:** A modern glassmorphism design with side-by-side input and multi-tab results dashboard.
- **Detailed Corrections:** Every suggestion includes the original phrase, the corrected phrase, the classification (grammar, spelling, punctuation, etc.), and the logical explanation.
- **Stylistic Rewrites:** Offers alternative phrasings based on context assumptions to improve the flow, tone, and voice.
- **Explainable LLM Feedback:** Diagnostic feedback summarizing the overall quality and focal points of the text.

---

## Project Structure

```text
├── app.py                      # FastAPI server and static file router
├── proofreader.py              # Core LLM interaction client & CLI demo
├── prompts.py                  # Pydantic schemas and system/user prompts
├── static/                     # Web application frontend assets
│   ├── index.html              # Modern dashboard layout
│   ├── style.css               # Clean vanilla CSS design
│   └── script.js               # Dynamic tab switching, API caller, UI rendering
├── .env                        # Environment credentials (REPLICATE_API_TOKEN)
└── README.md                   # Project documentation
```

---

## Tech Stack

- **Backend:** FastAPI, Uvicorn, Python 3.13+, Requests, Python-dotenv
- **Frontend:** Vanilla HTML5, CSS3, ES6 JavaScript, Lucide Icons, Google Fonts (Inter & Outfit)
- **Deployment & Package Tooling:** Managed via `uv` in WSL2

---

## Getting Started

### 1. Environment Setup

Copy `.envsample` to a new `.env` file in the root of the project and add your Replicate API Token:

```bash
cp .envsample .env
```

Edit the `.env` file:
```env
REPLICATE_API_TOKEN=your_replicate_token_here
```

### 2. Running the Application

This project is configured to run efficiently inside a WSL2 environment using `uv`.

#### Option A: Running the Web App (Recommended)
Start the FastAPI server:
```bash
uv run app.py
```
Once initialized, open your web browser and navigate to **`http://127.0.0.1:8000`**.

#### Option B: Running the CLI Demo
Run a diagnostic proofreading evaluation of sample text directly in the console:
```bash
uv run proofreader.py
```

