import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

# Точка входа YandexGPT v2
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
HEADERS = {
    "Authorization": f"Api-Key {API_KEY}",
    "x-folder-id": FOLDER_ID,
    "Content-Type": "application/json"
}

# Комплаенс-ориентированный промт
PAYLOAD = {
    "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
    "completionOptions": {
        "stream": False,
        "temperature": 0.3,  # Низкая "креативность" для точности
        "maxTokens": "512"
    },
    "messages": [
        {
            "role": "system",
            "text": "Вы — FinCompliance Assistant. Отвечайте строго по фактам. В конце добавляйте дисклеймер: 'Ответ носит справочный характер. Требуется верификация юристом.' Не выдумывайте статьи и нормативные акты."
        },
        {
            "role": "user",
            "text": "Какой основной федеральный закон регулирует противодействие отмыванию доходов в РФ? Укажи номер и дату принятия."
        }
    ]
}

print("📡 Отправляем запрос в YandexGPT...")
try:
    response = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=30)
    response.raise_for_status()  # Вызовет ошибку, если статус != 200
    
    data = response.json()
    answer = data.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "Нет ответа")
    
    # 📝 Формируем аудит-лог (обязательно для комплаенса)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": "yandexgpt",
        "folder_id": FOLDER_ID,
        "user_prompt": PAYLOAD["messages"][1]["text"],
        "system_prompt": PAYLOAD["messages"][0]["text"],
        "ai_response_full": answer,
        "status": "success"
    }
    
    with open("audit_log_step2.json", "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)
        
    print("✅ Ответ получен:")
    print("-" * 50)
    print(answer)
    print("-" * 50)
    print("📁 Аудит-лог сохранён: audit_log_step2.json")
    print("🚀 Шаг 2 выполнен успешно.")
    
except requests.exceptions.HTTPError as e:
    print(f"❌ Ошибка API: {response.status_code}")
    print(f"📄 Детали: {response.text}")
    print("💡 Подсказка: Если 401/403 → проверьте, что API-ключ активен и имеет права на YandexGPT.")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")