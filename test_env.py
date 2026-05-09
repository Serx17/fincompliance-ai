import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YANDEX_API_KEY")
folder_id = os.getenv("YANDEX_FOLDER_ID")

if not api_key or len(api_key) < 10:
    print("❌ ОШИБКА: YANDEX_API_KEY не найден или пустой.")
else:
    masked = api_key[:6] + "..." + api_key[-4:]
    print("✅ .env загружен успешно.")
    print(f"🔑 API_KEY: {masked}")
    print(f"📁 FOLDER_ID: {folder_id or 'Не указан'}")
    print("🚀 Окружение готово. Ждём подтверждения для Шага 2.")