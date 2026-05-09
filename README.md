# 🏦 FinCompliance Assistant (RU 2026)

AI-powered Compliance Co-Pilot for Russian Financial Regulation.  
Automates AML/KYC rule evaluation, generates regulator-ready reports with full AI traceability, and enforces Human-in-the-Loop controls.

## ⚡ Quick Start
```bash
git clone <your-repo-url>
cd fincompliance-ai
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Заполните YANDEX_API_KEY и FOLDER_ID
python run_pipeline.py

📐 Architecture
See docs/ARCHITECTURE.md for Mermaid diagrams & data flow.
🛡 Compliance & Security
rules/aml_rules.json — versioned, Pydantic-validated regulatory rules (115-ФЗ)
audit_*.jsonl — immutable, timestamped AI interaction logs
Temperature=0.2 + disclaimer injection — prevents LLM hallucination
Human-in-the-Loop by design: AI drafts, legal expert approves
📦 Tech Stack
Python 3.11+ | YandexGPT | Pydantic V2 | FastAPI-ready | Docker-ready | 115-ФЗ/152-ФЗ aligned
⚖️ Disclaimer
This project is a technical demonstration. It does not replace licensed legal counsel or official CB RF compliance procedures. All AI outputs require mandatory human verification.