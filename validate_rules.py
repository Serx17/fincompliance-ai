import json
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Literal

# 📋 Схема правила (гарантирует, что все поля на месте)
class ComplianceRule(BaseModel):
    rule_id: str = Field(..., min_length=5, description="Уникальный код правила")
    title: str = Field(..., min_length=10)
    description: str
    condition: str  # Пока строка, позже превратим в исполняемый код
    action: str
    source: str = Field(..., pattern=r"\d+-ФЗ|Указание ЦБ|ГОСТ")
    version: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}")  # YYYY-MM-DD
    severity: Literal["low", "medium", "high", "critical"]

    @validator('rule_id')
    def rule_id_must_start_with_aml(cls, v):
        if not v.startswith("AML_"):
            raise ValueError("rule_id должен начинаться с 'AML_'")
        return v

# 🔍 Загружаем и валидируем правила
def load_and_validate_rules(filepath: str) -> List[ComplianceRule]:
    with open(filepath, 'r', encoding='utf-8') as f:
        rules_data = json.load(f)
    
    validated = []
    for i, rule in enumerate(rules_data):
        try:
            validated_rule = ComplianceRule(**rule)
            validated.append(validated_rule)
            print(f"✅ Правило {i+1}: {validated_rule.rule_id} — валидно")
        except Exception as e:
            print(f"❌ Ошибка в правиле {i+1}: {e}")
    
    return validated

# 🚀 Запуск
if __name__ == "__main__":
    rules_file = Path("rules/aml_rules.json")
    if not rules_file.exists():
        print(f"❌ Файл не найден: {rules_file}")
    else:
        print(f"📚 Загружаем правила из {rules_file}...")
        rules = load_and_validate_rules(rules_file)
        print(f"\n🎯 Всего правил: {len(rules)}")
        print(f"📁 Валидация завершена. Правила готовы к использованию.")