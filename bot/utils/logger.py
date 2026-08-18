"""Логгер для записи действий модерации в PocketBase"""
from pocketbase import PocketBase
from config import settings

pb = PocketBase(settings.PB_URL)

def log_action(action: str, target_id: str, moderator_id: str, reason: str):
    """Функция для записи логов в PocketBase"""
    try:
        pb.collection("mod_logs").create({
            "action": action,
            "target_id": str(target_id),
            "moderator_id": str(moderator_id),
            "reason": str(reason)
        })
    except Exception as e:
        print(f"⚠️ Ошибка записи в PocketBase: {e}")
