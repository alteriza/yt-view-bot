# test_import.py
print("Testing imports...")

try:
    from bot.thorium_engine import ThoriumBot
    print("✓ ThoriumBot imported")
except Exception as e:
    print(f"✗ ThoriumBot error: {e}")

try:
    from bot.logger import BotLogger
    print("✓ BotLogger imported")
except Exception as e:
    print(f"✗ BotLogger error: {e}")

try:
    from bot.proxy_manager import ProxyManager
    print("✓ ProxyManager imported")
except Exception as e:
    print(f"✗ ProxyManager error: {e}")

try:
    from bot.anti_detect import get_stealth_user_agent
    print("✓ anti_detect imported")
except Exception as e:
    print(f"✗ anti_detect error: {e}")

print("Selesai test import")