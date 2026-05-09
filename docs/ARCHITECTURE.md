# 🏗 Architecture & Data Flow

## System Context
```mermaid
graph LR
  A[Data Sources<br>Mock/DB/API] --> B(Rule Engine)
  B --> C{Condition Met?}
  C -->|Yes| D[Risk Flags]
  C -->|No| E[Clean Transaction]
  D --> F[YandexGPT LLM]
  F --> G[Compliance Report + Disclaimer]
  G --> H[Audit Log JSONL]
  E --> H

  Key Guardrails
Safe Eval: Conditions execute in restricted sandbox (no os, import, network)
Pydantic V2: Strict schema validation for rules & flags
LLM Constraints: temperature=0.2, mandatory disclaimer, JSON/text fallback
Audit Chain: Every AI call logged with timestamp, prompt preview, model version, folder_id