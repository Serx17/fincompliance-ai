# 📜 Compliance & Regulatory Alignment (RU 2026)

## 115-ФЗ (ПОД/ФТ)
- Rules versioned & timestamped (`rules/aml_rules.json`)
- Thresholds match CB RF guidance (e.g., ≥600k RUB → enhanced KYC)
- Beneficial owner identification enforced for legal entities

## 152-ФЗ (ПДн)
- No PII stored in logs; transaction IDs used as pseudonyms
- `.env` strictly excluded via `.gitignore`
- YandexGPT processed via secure API (TLS 1.3, data residency RU)

## AI Audit & Human-in-the-Loop
- CB RF 2024-2025 guidelines require traceable AI decisions
- Every LLM output logged with prompt context, model version, timestamp
- System explicitly marks outputs as `requires_manual_review`
- Disclaimer auto-injected to prevent over-reliance on AI

## Limitations
- Rule conditions use Python syntax for demo; production requires DSL parser
- Mock data used; replace with DBO/CRM connectors for live deployment
- Does not replace certified compliance officer sign-off