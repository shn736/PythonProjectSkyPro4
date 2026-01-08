from django.core.cache import cache


def get_recipients_from_cache(user):
    key = f"recipients_{user.id}"
    return cache.get(key)


def cache_recipients(user, recipients):
    key = f"recipients_{user.id}"
    cache.set(key, recipients, timeout=60 * 15)


def get_messages_from_cache(user):
    """Получает данные из кэша"""
    key = f"messages_{user.id}"
    return cache.get(key)


def cache_messages(user, messages):
    key = f"messages_{user.id}"
    cache.set(key, messages, timeout=60 * 15)


def get_newsletters_from_cache(user):
    """Получает данные из кэша"""
    key = f"newsletters_{user.id}"
    return cache.get(key)


def cache_newsletters(user, newsletters):
    key = f"newsletters_{user.id}"
    cache.set(key, newsletters, timeout=60 * 15)
