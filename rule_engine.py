import json
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Any, Dict
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)  # Убираем жёлтые предупреждения

# 📋 Схема правила (обновлённая под Pydantic V2)
class ComplianceRule(BaseModel):
    rule_id: str = Field(..., min_length=5)
    title: str = Field(..., min_length=10)
    description: str
    condition: str
    action: str
    source: str = Field(..., pattern=r"\d+-ФЗ|Указание ЦБ|ГОСТ")
    version: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}")
    severity: Literal["low", "medium", "high", "critical"]

    @field_validator('rule_id')
    @classmethod
    def rule_id_must_start_with_aml(cls, v):
        if not v.startswith("AML_"):
            raise ValueError("rule_id должен начинаться с 'AML_'")
        return v

# 🚩 Результат проверки
class RiskFlag(BaseModel):
    rule_id: str
    severity: str
    reason: str
    source: str
    transaction_id: str

# 🔍 Безопасная проверка условия (песочница)
def safe_eval(condition: str, data: Dict[str, Any]) -> bool:
    """Выполняет только безопасные выражения: сравнения, логика, числа"""
    allowed_names = {k: v for k, v in data.items()}
    allowed_builtins = {
        'True': True, 'False': False, 'None': None,
        'and': None, 'or': None, 'not': None  # логика
    }
    try:
        # Преобразуем условие в исполняемый код
        code = compile(condition, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names and name not in allowed_builtins:
                raise NameError(f"Запрещённое имя: {name}")
        return eval(code, {"__builtins__": {}}, allowed_names)
    except Exception as e:
        print(f"⚠️ Ошибка в условии '{condition}': {e}")
        return False

# 🎯 Главная функция: применить правила к данным
def evaluate_transaction(transaction: Dict[str, Any], rules: List[ComplianceRule]) -> List[RiskFlag]:
    flags = []
    for rule in rules:
        if safe_eval(rule.condition, transaction):
            flag = RiskFlag(
                rule_id=rule.rule_id,
                severity=rule.severity,
                reason=rule.description,
                source=rule.source,
                transaction_id=transaction.get("transaction_id", "unknown")
            )
            flags.append(flag)
            print(f"🚩 Сработало правило [{rule.rule_id}]: {rule.title}")
    return flags

# 🧪 Тестовые данные (mock)
MOCK_TRANSACTIONS = [
    {
        "transaction_id": "TXN-001",
        "transaction_amount": 750000,  # >600k → должно сработать правило
        "client_kyc_status": "pending",
        "client_type": "individual",
        "beneficial_owner_verified": None
    },
    {
        "transaction_id": "TXN-002",
        "transaction_amount": 150000,  # <600k → правило не сработает
        "client_kyc_status": "verified",
        "client_type": "legal",
        "beneficial_owner_verified": False  # → сработает правило про бенефициара
    }
]

# 🚀 Запуск
if __name__ == "__main__":
    # 1. Загружаем правила
    rules_file = Path("rules/aml_rules.json")
    with open(rules_file, 'r', encoding='utf-8') as f:
        rules_data = json.load(f)
    rules = [ComplianceRule(**r) for r in rules_data]
    print(f"📚 Загружено {len(rules)} правил\n")
    
    # 2. Проверяем каждую тестовую транзакцию
    for txn in MOCK_TRANSACTIONS:
        print(f"\n🔍 Проверяем транзакцию: {txn['transaction_id']}")
        print(f"   Сумма: {txn['transaction_amount']} ₽, KYC: {txn['client_kyc_status']}")
        flags = evaluate_transaction(txn, rules)
        if not flags:
            print("✅ Рисков не обнаружено")
        else:
            print(f"⚠️ Найдено флагов: {len(flags)}")
            for flag in flags:
                print(f"   • [{flag.severity.upper()}] {flag.rule_id}: {flag.reason}")
                print(f"     Источник: {flag.source}")
    
    print("\n🎯 Rule Engine тест завершён.")