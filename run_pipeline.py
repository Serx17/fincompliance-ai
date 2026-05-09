import os, json, requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

# 🔑 Настройки
API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# 📋 Модели данных
class Rule(BaseModel):
    rule_id: str = Field(..., min_length=5)
    title: str
    description: str
    condition: str
    source: str
    version: str
    severity: str
    @field_validator('rule_id')
    @classmethod
    def check_aml(cls, v): return v if v.startswith("AML_") else ValueError("Start with AML_")

class Flag(BaseModel):
    rule_id: str; severity: str; reason: str; source: str; txn_id: str

# 🔍 Безопасный eval
def safe_eval(cond: str, data: Dict[str, Any]) -> bool:
    allowed = dict(data)
    try:
        code = compile(cond, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed and name not in ("True","False","None"): return False
        return eval(code, {"__builtins__": {}}, allowed)
    except: return False

# 🧠 AI-запрос
def ask_gpt(flags: List[Flag], txn: Dict) -> str:
    prompt = f"Транзакция {txn['txn_id']}: {txn['amount']}₽, KYC={txn['kyc']}, Тип={txn['type']}. Правила: {json.dumps([f.model_dump() for f in flags], ensure_ascii=False, indent=2)}. Сформируйте краткий комплаенс-отчёт. Укажите нормы, риск, рекомендацию. В конце: 'Ответ носит справочный характер. Требуется верификация юристом.'"
    headers = {"Authorization": f"Api-Key {API_KEY}", "x-folder-id": FOLDER_ID, "Content-Type": "application/json"}
    payload = {"modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest", "completionOptions": {"stream": False, "temperature": 0.2, "maxTokens": "1024"}, "messages": [{"role": "system", "text": "Эксперт по фин. комплаенсу РФ. Только факты."}, {"role": "user", "text": prompt}]}
    try:
        r = requests.post(GPT_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json().get("result",{}).get("alternatives",[{}])[0].get("message",{}).get("text","Ошибка AI")
    except Exception as e: return f"⚠️ AI недоступен: {e}. Требуется ручная проверка."

# 💾 Аудит
def log_audit(txn_id, flags, ai_text):
    entry = {"ts": datetime.now().isoformat(), "txn": txn_id, "flags": [f.model_dump() for f in flags], "ai": ai_text}
    with open("audit_pipeline.jsonl", "a", encoding="utf-8") as f: f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# 🚀 Запуск
if __name__ == "__main__":
    print("🏦 FinCompliance Pipeline v1.0 | RU 2026\n")
    
    rules_path = Path("rules/aml_rules.json")
    rules = [Rule(**r) for r in json.loads(rules_path.read_text(encoding="utf-8"))]
    print(f"📚 Загружено правил: {len(rules)}")
    
    txns = [
        {"txn_id": "TXN-001", "amount": 750000, "kyc": "pending", "type": "phys", "bo_verified": None},
        {"txn_id": "TXN-002", "amount": 150000, "kyc": "verified", "type": "legal", "bo_verified": False}
    ]
    
    for t in txns:
        print(f"\n🔍 {t['txn_id']} | {t['amount']}₽ | KYC: {t['kyc']}")
        # Преобразуем ключи под условия правил
        data = {"transaction_amount": t["amount"], "client_kyc_status": t["kyc"], "client_type": t["type"], "beneficial_owner_verified": t["bo_verified"], "transaction_id": t["txn_id"]}
        
        flags = [Flag(rule_id=r.rule_id, severity=r.severity, reason=r.description, source=r.source, txn_id=t["txn_id"]) for r in rules if safe_eval(r.condition, data)]
        
        if not flags:
            print("✅ Рисков нет")
            log_audit(t["txn_id"], [], "Чисто.")
            continue
            
        print(f"🚩 Флагов: {len(flags)}")
        print("🤖 Генерация отчёта...")
        report = ask_gpt(flags, t)
        print("-" * 70)
        print(report)
        print("-" * 70)
        log_audit(t["txn_id"], flags, report)
        
    print("\n🏁 Пайплайн завершён. Аудит: audit_pipeline.jsonl")