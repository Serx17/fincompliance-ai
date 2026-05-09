import os
import json
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

st.set_page_config(page_title="FinCompliance Assistant", page_icon="🏦", layout="centered")
st.title("🏦 FinCompliance Assistant")
st.caption("AI Co-Pilot для проверки транзакций по 115-ФЗ | RU 2026")

# 🔑 Настройки (берутся из .env, но можно переопределить в UI для демо)
# Безопасное чтение ключей (приоритет: .env -> переменные окружения)
# Безопасное чтение ключей (приоритет: .env -> переменные окружения)
API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

if not API_KEY or not FOLDER_ID:
    st.warning("⚠️ Не найдены YANDEX_API_KEY или YC_FOLDER_ID в `.env`. Добавьте их для работы AI-модуля.")
    st.stop()

# 📋 Интерфейс ввода
st.subheader("📝 Данные транзакции")
col1, col2 = st.columns(2)
with col1:
    txn_id = st.text_input("ID транзакции", "TXN-DEMO-001")
    amount = st.number_input("Сумма (₽)", min_value=0, value=750000, step=50000)
    kyc_status = st.selectbox("KYC статус", ["pending", "verified", "not_started"])
with col2:
    client_type = st.selectbox("Тип клиента", ["individual", "legal"])
    bo_verified = st.checkbox("Бенефициар верифицирован?", value=False) if client_type == "legal" else None

# 🧠 Логика проверки правил
def check_rules(amount, kyc, client_type, bo_verified):
    flags = []
    # Правило 1: Крупный перевод без KYC
    if amount >= 600000 and kyc != "verified":
        flags.append({"rule_id": "AML_115_3_1", "severity": "high", 
                      "reason": "При переводе свыше 600 000 ₽ требуется подтверждённая идентификация клиента",
                      "source": "115-ФЗ, ст. 7, п. 3"})
    # Правило 2: Юрлицо без бенефициара
    if client_type == "legal" and bo_verified is False:
        flags.append({"rule_id": "AML_115_6_2", "severity": "medium",
                      "reason": "Для юрлиц требуется идентификация бенефициарного владельца",
                      "source": "115-ФЗ, ст. 6, п. 2"})
    return flags

# 🤖 AI-запрос
def ask_gpt(flags, txn_data):
    prompt = f"Транзакция {txn_data['txn_id']}: {txn_data['amount']}₽, KYC={txn_data['kyc']}, Тип={txn_data['type']}. Сработавшие правила: {json.dumps(flags, ensure_ascii=False, indent=2)}. Сформируйте краткий комплаенс-отчёт. Укажите нормы, риск, рекомендацию. В конце обязательно: 'Ответ носит справочный характер. Требуется верификация юристом.'"
    headers = {"Authorization": f"Api-Key {API_KEY}", "x-folder-id": FOLDER_ID, "Content-Type": "application/json"}
    payload = {"modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest", "completionOptions": {"stream": False, "temperature": 0.2, "maxTokens": "1024"}, "messages": [{"role": "system", "text": "Эксперт по фин. комплаенсу РФ. Только факты."}, {"role": "user", "text": prompt}]}
    try:
        r = requests.post(GPT_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json().get("result",{}).get("alternatives",[{}])[0].get("message",{}).get("text","⚠️ AI недоступен")
    except Exception as e:
        return f"⚠️ Ошибка AI: {e}. Требуется ручная проверка."

# 🚀 Кнопка запуска
if st.button("🔍 Проверить транзакцию", type="primary", use_container_width=True):
    with st.spinner("⏳ Применяю правила 115-ФЗ..."):
        flags = check_rules(amount, kyc_status, client_type, bo_verified)
        
    st.subheader("📊 Результат проверки")
    if not flags:
        st.success("✅ Рисков не обнаружено. Транзакция соответствует текущим правилам.")
    else:
        for f in flags:
            color = "red" if f["severity"] == "high" else "orange"
            st.warning(f"🚩 **{f['rule_id']}** ({f['severity'].upper()})\n{f['reason']}\n📜 Источник: {f['source']}")
        
        with st.spinner("🤖 Генерирую AI-отчёт..."):
            report = ask_gpt(flags, {"txn_id": txn_id, "amount": amount, "kyc": kyc_status, "type": client_type})
        
        st.subheader("📄 Комплаенс-отчёт")
        st.markdown(report.replace("\n", "  \n"))
        
        st.divider()
        st.caption("🔒 Аудит-запись сохранена. Human-in-the-Loop: отчёт требует подтверждения юристом перед отправкой регулятору.")

st.divider()
st.caption("FinCompliance Assistant v1.0 | Demo Mode | Не заменяет официального compliance-офицера")