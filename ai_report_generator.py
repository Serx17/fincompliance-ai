import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# 📋 Модель флага риска (для типизации)
class RiskFlag(BaseModel):
    rule_id: str
    severity: str
    reason: str
    source: str
    transaction_id: str

# 📋 Модель итогового отчёта
class ComplianceReport(BaseModel):
    transaction_id: str
    generated_at: str
    summary: str
    findings: List[dict]
    recommendations: str
    disclaimer: str = Field(default="Ответ носит справочный характер. Требуется верификация юристом.")

# 🧠 Формируем промт для YandexGPT
def build_prompt(flags: List[RiskFlag], transaction: dict) -> str:
    flags_text = "\n".join([
        f"- [{f.severity.upper()}] {f.rule_id}: {f.reason}\n  Источник: {f.source}"
        for f in flags
    ])
    
    return f"""Вы — эксперт по комплаенсу в финансовой сфере РФ.
Сформируйте краткий отчёт для внутреннего аудита по транзакции.

ДАННЫЕ ТРАНЗАКЦИИ:
• ID: {transaction.get('transaction_id')}
• Сумма: {transaction.get('transaction_amount', 'N/A')} ₽
• Тип клиента: {transaction.get('client_type', 'N/A')}
• KYC-статус: {transaction.get('client_kyc_status', 'N/A')}

СРАБОТАВШИЕ ПРАВИЛА:
{flags_text}

ТРЕБОВАНИЯ К ОТЧЁТУ:
1. Кратко опишите суть риска (1-2 предложения)
2. Укажите, какие нормы закона нарушены/под вопросом
3. Дайте рекомендацию: «требуется ручная проверка» / «документы запрошены» / «риск снят»
4. В конце добавьте дисклеймер: «Ответ носит справочный характер. Требуется верификация юристом.»
5. Отвечайте на русском, профессионально, без воды.

Выведите ответ в формате чистого текста, без JSON-обёртки."""

# 🤖 Запрос к YandexGPT
def call_yandexgpt(prompt: str) -> Optional[str]:
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "x-folder-id": FOLDER_ID,
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,  # Минимум креатива, максимум точности
            "maxTokens": "1024"
        },
        "messages": [
            {"role": "system", "text": "Вы — помощник по комплаенсу. Отвечайте строго по фактам, цитируйте источники."},
            {"role": "user", "text": prompt}
        ]
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        data = response.json()
        return data.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text")
    except Exception as e:
        print(f"❌ Ошибка вызова YandexGPT: {e}")
        return None

# 📝 Генерация отчёта + сохранение аудита
def generate_compliance_report(flags: List[RiskFlag], transaction: dict) -> Optional[dict]:
    if not flags:
        return {"status": "no_risks", "message": "Рисков не обнаружено, отчёт не требуется"}
    
    prompt = build_prompt(flags, transaction)
    print("🤖 Генерирую пояснения через YandexGPT...")
    ai_text = call_yandexgpt(prompt)
    
    if not ai_text:
        print("⚠️ Не удалось получить ответ от AI, возвращаю шаблон")
        ai_text = f"Транзакция {transaction.get('transaction_id')} требует ручной проверки по правилам: {[f.rule_id for f in flags]}. Ответ носит справочный характер. Требуется верификация юристом."
    
    # 📁 Сохраняем аудит-лог
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "transaction_id": transaction.get("transaction_id"),
        "flags_triggered": [f.model_dump() for f in flags],
        "ai_prompt_preview": prompt[:200] + "...",
        "ai_response": ai_text,
        "model_version": "yandexgpt/latest",
        "folder_id": FOLDER_ID
    }
    
    # Добавляем в общий лог-файл (append-режим)
    with open("audit_log_full.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
    
    return {
        "transaction_id": transaction.get("transaction_id"),
        "generated_at": audit_entry["timestamp"],
        "report_text": ai_text,
        "audit_file": "audit_log_full.jsonl"
    }

# 🧪 Тестовые данные (те же, что в rule_engine.py)
MOCK_TRANSACTIONS = [
    {
        "transaction_id": "TXN-001",
        "transaction_amount": 750000,
        "client_kyc_status": "pending",
        "client_type": "individual",
        "beneficial_owner_verified": None
    },
    {
        "transaction_id": "TXN-002",
        "transaction_amount": 150000,
        "client_kyc_status": "verified",
        "client_type": "legal",
        "beneficial_owner_verified": False
    }
]

# 🚀 Запуск демо
if __name__ == "__main__":
    print("🚀 Запуск AI Report Generator (демо-режим)\n")
    
    # Для демо создаём флаги вручную (в реальности они придут из rule_engine.py)
    demo_flags = {
        "TXN-001": [
            RiskFlag(
                rule_id="AML_115_3_1",
                severity="high",
                reason="При переводе свыше 600 000 ₽ требуется подтверждённая идентификация клиента",
                source="115-ФЗ, ст. 7, п. 3",
                transaction_id="TXN-001"
            )
        ],
        "TXN-002": [
            RiskFlag(
                rule_id="AML_115_6_2",
                severity="medium",
                reason="Для юрлиц требуется идентификация бенефициарного владельца",
                source="115-ФЗ, ст. 6, п. 2",
                transaction_id="TXN-002"
            )
        ]
    }
    
    for txn in MOCK_TRANSACTIONS:
        tid = txn["transaction_id"]
        print(f"\n📄 Генерируем отчёт для {tid}...")
        flags = demo_flags.get(tid, [])
        result = generate_compliance_report(flags, txn)
        
        if result and result.get("report_text"):
            print("✅ Отчёт сгенерирован:")
            print("-" * 60)
            print(result["report_text"])
            print("-" * 60)
            print(f"📁 Аудит сохранён в: {result['audit_file']}")
    
    print("\n🎯 Демо AI Report Generator завершено.")