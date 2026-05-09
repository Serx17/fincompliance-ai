# 🏦 FinCompliance Assistant (RU 2026)

**AI Co-Pilot для финансового комплаенса**  
Автоматическая проверка транзакций на соответствие 115-ФЗ, генерация отчётов с трассировкой AI и Human-in-the-Loop контролем.

## 🚀 Быстрый старт
Запуск веб-интерфейса (демо за 1 минуту):
```bash
git clone https://github.com/Serx17/fincompliance-ai.git
cd fincompliance-ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Создайте файл .env и добавьте YANDEX_API_KEY и FOLDER_ID
streamlit run app.py

🏗 Архитектура
Проект построен по принципам Compliance-by-Design:
Rule Engine: Машиночитаемые правила в rules/aml_rules.json (Pydantic validation).
AI Generation: YandexGPT генерирует отчёт с температурой 0.2 (минимум галлюцинаций).
Audit Trail: Все запросы логируются в JSONL с метками времени и версиями моделей.
Safety: Изолированное исполнение условий (safe_eval), строгие промпты, дисклеймеры.
Скриншоты
<img width="407" height="391" alt="1" src="https://github.com/user-attachments/assets/be6696f1-185c-4c9b-8761-b6214eece972" />




⚖️ Disclaimer
Это демонстрационный проект (Proof of Concept). Не предназначен для реального использования в боевом контуре без аудита безопасности.

