import os
import json
import threading
from flask import Flask
from telethon import TelegramClient, events

# --- تشغيل ويب سيرفر وهمي لتخطي شروط الاستضافة المجانية في Render ---
app = Flask('')
@app.route('/')
def home(): 
    return "🚀 Bot is alive and running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# تشغيل السيرفر الوهمي في الخلفية
threading.Thread(target=run_web, daemon=True).start()

# --- بيانات المطور والاتصال المعتمدة الخاصة بك ---
API_ID = 33498297         
API_HASH = 'b2bd511af02044f258f55d31da4f505f'  
BOT_TOKEN = '8836423442:AAEEA2wb_A1uWNq9fawDfQOICrRgw9NAn3Y'
OWNER_ID = 8345423142

# بدء تشغيل البوت
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- نظام الحفظ الدائم (JSON) ---
DATA_FILE = "bot_settings.json"

def load_settings():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return (
                    data.get("dnd", False), 
                    set(data.get("muted", [])), 
                    set(data.get("blocked", [])),
                    set(data.get("admins", []))
                )
        except Exception:
            pass
    return False, set(), set(), set()

def save_settings():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "dnd": DO_NOT_DISTURB,
                "muted": list(MUTED_USERS),
                "blocked": list(BLOCKED_USERS),
                "admins": list(ALLOWED_ADMINS)
            }, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ فشل حفظ الإعدادات: {e}")

DO_NOT_DISTURB, MUTED_USERS, BLOCKED_USERS, ALLOWED_ADMINS = load_settings()

@client.on(events.NewMessage)
async def handle_messages(event):
    global DO_NOT_DISTURB, MUTED_USERS, BLOCKED_USERS, ALLOWED_ADMINS
    
    sender_id = event.sender_id
    message_text = event.raw_text.strip() if event.raw_text else ""

    is_owner = (sender_id == OWNER_ID)
    is_admin = sender_id in ALLOWED_ADMINS
    
    if is_owner or is_admin:
        if is_owner:
            if message_text == ".إضافة مشرف" and event.is_private:
                ALLOWED_ADMINS.add(event.chat_id)
                save_settings()
                await event.reply("➕ تم منح هذا المستخدم صلاحية مشرف في البوت بنجاح.")
                return
            elif message_text == ".إزالة مشرف" and event.is_private:
                ALLOWED_ADMINS.discard(event.chat_id)
                save_settings()
                await event.reply("➖ تم إلغاء صلاحية الإشراف عن هذا المستخدم.")
                return

        if message_text == ".تفعيل الهدوء":
            DO_NOT_DISTURB = True
            save_settings()
            await event.reply("🤫 تم تفعيل وضع (عدم الإزعاج). سيتوقف البوت عن الرد تلقائياً.")
            return
        elif message_text == ".إلغاء الهدوء":
            DO_NOT_DISTURB = False
            save_settings()
            await event.reply("🔔 تم إلغاء وضع عدم الإزعاج. عاد البوت للرد التلقائي.")
            return
        elif message_text == ".كتم" and event.is_private:
            MUTED_USERS.add(event.chat_id)
            save_settings()
            await event.reply("🤐 تم كتم هذا المستخدم داخل البوت.")
            return
        elif message_text == ".الغاء الكتم" and event.is_private:
            MUTED_USERS.discard(event.chat_id)
            save_settings()
            await event.reply("🔊 تم إلغاء الكتم عن هذا المستخدم.")
            return
        elif message_text == ".حظر" and event.is_private:
            BLOCKED_USERS.add(event.chat_id)
            save_settings()
            await event.reply("🚫 تم حظر المستخدم تماماً من استخدام البوت.")
            return
        elif message_text == ".الغاء الحظر" and event.is_private:
            BLOCKED_USERS.discard(event.chat_id)
            save_settings()
            await event.reply("✅ تم إلغاء الحظر عن هذا المستخدم.")
            return

    if event.is_private:
        if not is_admin and not is_owner:
            if sender_id in BLOCKED_USERS or DO_NOT_DISTURB or sender_id in MUTED_USERS:
                return

        msg_lower = message_text.lower()
        if any(word in msg_lower for word in ['مرحبا', 'السلام عليكم', 'هلا', 'هلو']):
            try:
                sender = await event.get_sender()
                name = sender.first_name if sender else "العزيز"
                await event.reply(f"أهلاً بك {name}! 🤖 أنا البوت المساعد للمطور.")
            except Exception as e:
                print(f"⚠️ خطأ أثناء إرسال الرد: {e}")

print("🚀 البوت يعمل الآن ومربوط بحساب المطور بنجاح على السيرفر السحابي...")
client.run_until_disconnected()
