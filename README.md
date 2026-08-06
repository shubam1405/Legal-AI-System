# 🏛️ AI Legal Assistant & Lawyer Matchmaker (CrewAI & Streamlit)

A comprehensive, state-of-the-art AI-powered Legal Assistant platform designed to bridge the gap between citizens seeking legal help and legal professionals streamlining their workflow. The system integrates a robust **Multi-Agent Architecture** using **CrewAI**, advanced **Retrieval-Augmented Generation (RAG)** via **ChromaDB**, and a dynamic, multilingual **Streamlit** UI.

---

## 🌟 Core Features

### 👥 For the Public (Citizens)
- **🌍 Multilingual AI Legal Chatbot:** Users can chat in multiple regional languages (Hindi, Telugu, Tamil, Marathi, Bengali, etc.). The system auto-translates queries to English for the LLM, and translates responses back to the user's native language using `deep-translator`.
- **⚖️ AI Lawyer Matchmaker:** Users describe their case, and an LLM-based suggestion system analyzes the case context to extract semantic requirements, matching them with the most suitable vetted lawyers in the database.
- **📄 Legal Templates:** Access and understand pre-formatted common legal templates (e.g., Non-Disclosure Agreements, Eviction Notices).
- **📂 Document Understanding:** Users can upload context files to the chatbot to ask questions specifically about their uploaded legal documents.

### 💼 For Legal Professionals (Lawyers)
- **🔐 Authenticated Dashboard:** Lawyers can log in to view their matched cases.
- **🤖 Autonomous AI Workflows (CrewAI):** Lawyers can trigger an AI crew to process a case. The multi-agent crew handles:
  1. *Case Intake & Analysis*
  2. *IPC Section Retrieval* (Fetching relevant Indian Penal Code laws)
  3. *Legal Precedent Search* (Finding relevant historical case laws)
  4. *Legal Drafting* (Drafting notices and appeals based on the previous agents' findings) 

---

## 🏗️ System Architecture & Algorithms

### 1. Multi-Agent Orchestration (CrewAI)
The core intelligence of the backend is driven by **CrewAI**. Instead of relying on a single monolithic prompt, the system breaks down complex legal tasks into specialized autonomous agents:
*   **Case Intake Agent:** Reads the raw user description, cleans it, and identifies key legal domain topics.
*   **IPC Section Agent:** Armed with a Custom Tool mapping to a Vector DB (`tools/ipc_sections_search_tool.py`), it searches the `ipc.json` database for matching penal codes.
*   **Legal Precedent Agent:** Searches historical data for similar case decisions.
*   **Legal Drafter Agent:** Compiles the findings from all previous agents to generate a structured legal draft (e.g., Legal Notice or Bail Plea).

### 2. Retrieval-Augmented Generation (RAG) algorithm
To prevent hallucinations (hallucinating fake laws), the system utilizes **ChromaDB** to index real legal texts.
*   **Chunking & Embedding:** Legal documents and standard IPC sections are split into chunks. Embeddings are generated (typically using Google Generative AI / Gemini models) and stored in Chroma.
*   **Semantic Search:** When an agent needs a law, it performs a similarity search in the multidimensional vector space, fetching the exact text from `ipc.json` and injecting it directly into its context window.

### 3. Localization Pipeline (Live Translation)
To maintain high context accuracy for the AI, the system runs a double-translation proxy:
*   User Input -> Detected Language -> `deep-translator` -> English -> LLM processing -> English Output -> `deep-translator` -> Original Language -> UI Display.

---

## 💻 Tech Stack

| Domain | Technology/Library | Purpose |
| ------ | ------------------ | ------- |
| **Frontend UI** | Streamlit | Rapid, state-driven, dynamic user interface. |
| **AI Agents** | CrewAI | Multi-agent orchestration and task delegation. |
| **LLM Provider** | Google Gemini (via Custom APIs) | Core reasoning, text generation, and embeddings. |
| **Vector DB** | ChromaDB (SQLite local) | Local vector storage for semantic legal search. |
| **NoSQL DB** | MongoDB | Storing standard application data (Lawyer profiles, Case history). |
| **Utilities** | Deep-Translator, Pydantic | Live language translation and structured data validation. |

---

## 🗂️ Detailed Project Structure

```text
ai-legal-assistant-crewai/
│
├── 🚀 Root Application Files
│   ├── app.py                   # Main entry point for Streamlit. Handles routing mechanics and session states.
│   ├── public_ui.py             # Public-facing modules: Chatbot UI, Matchmaker, file-upload widgets, directory.
│   ├── auth_ui.py               # Authentication barrier, login system, and the Lawyer/Advocate dashboard UI.
│   ├── components.py            # Reusable UI Streamlit widgets (cards, metrics, custom layouts).
│   ├── styles.py                # Pure CSS style injections for Streamlit cleanup.
│   ├── config.py                # System-wide configuration constants (DB URIs, file paths, model names).
│   └── main.py                  # CLI executable to test CrewAI flows without starting the Streamlit UI.
│
├── 🧠 AI & Core Business Logic
│   ├── ai_service.py            # Primary service layer for standard LLM calls, handling translations, and the Lawyer Matchmaking algorithm.
│   ├── crew.py                  # Orchestrates the CrewAI setup: links agents with tasks and initializes the sequential process.
│   ├── case_manager.py          # Handles the business logic of saving, updating, and associating Cases with Lawyers in MongoDB.
│   └── mongo_service.py         # Direct database repository layer establishing the connection/CRUD operations to MongoDB.
│
├── 📚 Vector Database Management
│   ├── document_vectordb.py     # Script to ingest user-uploaded PDFs/TXts, chunk them, embed, and save to Chroma.
│   ├── ipc_vectordb_builder.py  # A specialized script to convert the massive `ipc.json` into semantic vector embeddings.
│   └── ipc.json                 # Unstructured/Structured massive JSON containing all Indian Penal Code data.
│
├── 🤖 CrewAI Modules
│   ├── agents/                  # Definitions for AI personas (Case Intake, Drafter, etc.) setting their goals and backstories.
│   ├── tasks/                   # Task definitions mapping specifically *what* an agent must do and its expected output.
│   └── tools/                   # Custom Python classes inheriting from `BaseTool` allowing agents to interact with ChromaDB.
│
├── 🗄️ Data & Mock Information
│   ├── seed_lawyers.py          # A deployment utility to inject fake, highly detailed lawyer profiles into MongoDB.
│   ├── data/                    # Storage directory for persistent SQLite representations of Chroma and local document uploads.
│   └── sample_cases/            # Text files containing mock cases to test the system.
│
└── 📝 Documentation
    └── docs/                    # Architectural decisions, UI simplification plans, and deployment guides.
```

---

## ⚙️ How the Internal System Flow Works

### Scenario: Public User looking for legal help
1. **Interaction:** User opens `app.py`, navigates to "AI Matchmaker" (rendered by `public_ui.py`).
2. **Submission:** User writes their case in their native language context.
3. **Processing (`ai_service.py`):** The app passes the text to `suggest_lawyers_for_case()`. The LLM attempts to identify domains (e.g., "Family Law", "Criminal"). 
4. **Data Fetching:** Standard `mongo_service.py` fetches the lawyers. The AI maps the extracted domains to the lawyer's `specialization` and generates a `"match_reasoning"`.
5. **UI Update:** Streamlit triggers a `st.rerun()`, displaying dynamically generated cards for matched lawyers.

### Scenario: Lawyer Processing a Matched Case
1. **Authentication:** Lawyer logs in via `auth_ui.py`.
2. **Dashboard:** System queries MongoDB for cases assigned to this lawyer's `bar_council_id`.
3. **Execution (`crew.py`):** Lawyer clicks "Run AI Analysis". The system initializes the Crew process.
4. **Agent Handoffs:**
   - **Agent 1** (Intake) reads the case details and writes a summary.
   - **Agent 2** (IPC Search) reads the summary, uses its `ipc_sections_search_tool` (which queries ChromaDB vectors built by `ipc_vectordb_builder.py`), and retrieves exact laws.
   - **Agent 3 & 4** build upon this to write the final document.
5. **Completion:** The final Markdown results are streamed back to the Streamlit UI and stored contextually.

---

## 🛠️ Setup & Installation

1. **Clone the repository.**
2. **Create a virtual environment:** `python -m venv venv`
3. **Activate environment:** `.\venv\Scripts\Activate.ps1` (Windows)
4. **Install dependencies:** `pip install -r requirements.txt`
5. **Environment Variables:** Set up a `.env` file with `GEMINI_API_KEY` (or respective LLM key) and `MONGO_URI`.
6. **Seed Database:** Run `python seed_lawyers.py` and `python ipc_vectordb_builder.py` to prime the system.
7. **Run application:** `streamlit run app.py`

---
*Built with ❤️ utilizing Python, Streamlit, and CrewAI.*