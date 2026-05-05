import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1127663898"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "Winshade04")

DATA_FILE = "data.json"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Default groups (admin manages these)
DEFAULT_GROUPS_FILE = "default_groups.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}, "approved": [], "pending": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_default_groups():
    try:
        with open(DEFAULT_GROUPS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_default_groups(groups):
    with open(DEFAULT_GROUPS_FILE, "w") as f:
        json.dump(groups, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    
    # Save user info
    data["users"][str(user.id)] = {
        "name": user.full_name,
        "username": user.username or ""
    }
    save_data(data)
    
    keyboard = [
        [InlineKeyboardButton("📋 Features", callback_data="features")],
        [InlineKeyboardButton("📞 Admin ဆက်သွယ်ရန်", url=f"https://t.me/{ADMIN_USERNAME}")],
    ]
    
    # Show forward button only for approved users
    if str(user.id) in data.get("approved", []):
        keyboard.insert(1, [InlineKeyboardButton("📤 Forward Post", callback_data="forward_guide")])
        keyboard.insert(2, [InlineKeyboardButton("📂 My Groups", callback_data="my_groups")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🚀 𝗔𝘂𝘁𝗼 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗕𝗼𝘁\n\n"
        "ကိုယ့် Channel post တွေကို Group တွေထဲ\n"
        "Auto Share ပေးတဲ့ Bot ဖြစ်ပါတယ်။\n\n"
        "✅ Features ကြည့်ရန် အောက်က button နှိပ်ပါ။"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    # Notify admin about new user
    if str(user.id) not in data.get("approved", []) and str(user.id) not in data.get("pending", []):
        try:
            username = f"@{user.username}" if user.username else "No username"
            notify_text = (
                f"👤 New User!\n"
                f"Name: {user.full_name}\n"
                f"Username: {username}\n"
                f"ID: {user.id}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=notify_text)
        except:
            pass

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "features":
        features_text = (
            "🔥 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀\n\n"
            "📤 Auto Forward - Post ရွေးပြီး Group တွေထဲ Share\n"
            "📂 Default 3 Groups - ကျနော်တို့ဘက်က ပေးထားတဲ့ Group\n"
            "➕ Custom Groups - ကိုယ်တိုင် Group ထပ်ထည့်\n"
            "🔄 Ban Replace - Ban ဖြစ်ရင် Group အသစ် ပြောင်းပေး\n"
            "📞 24/7 Support\n\n"
            "သုံးချင်ရင် Admin ကို ဆက်သွယ်ပါ 👇"
        )
        keyboard = [[InlineKeyboardButton("📞 Admin ဆက်သွယ်ရန်", url=f"https://t.me/{ADMIN_USERNAME}")]]
        await query.edit_message_text(features_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "forward_guide":
        guide_text = (
            "📤 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗻𝗲𝗻𝗻𝗲\n\n"
            "1️⃣ ကိုယ့် Channel post ကို ဒီ bot ဆီ Forward လုပ်ပါ\n"
            "2️⃣ Bot က ကိုယ့် Group တွေထဲ Auto Share ပေးပါမယ်\n\n"
            "⚡ Forward လုပ်လိုက်ရုံပဲ - ကျန်တာ Bot အလုပ်!"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        await query.edit_message_text(guide_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "my_groups":
        user_id = str(query.from_user.id)
        data = load_data()
        user_data = data.get("user_groups", {}).get(user_id, [])
        default_groups = load_default_groups()
        
        # Show assigned default groups (first 3)
        assigned = default_groups[:3] if default_groups else []
        
        text = "📂 𝗠𝘆 𝗚𝗿𝗼𝘂𝗽𝘀\n\n"
        text += "📌 Default Groups:\n"
        if assigned:
            for i, g in enumerate(assigned, 1):
                text += f"  {i}. {g.get('name', 'Group')} {'✅' if g.get('active') else '❌ Ban'}\n"
        else:
            text += "  မရှိသေးပါ\n"
        
        text += "\n➕ Custom Groups:\n"
        if user_data:
            for i, g in enumerate(user_data, 1):
                text += f"  {i}. {g.get('name', 'Group')}\n"
        else:
            text += "  မရှိသေးပါ\n"
        
        text += "\n\nCustom Group ထည့်ရန်: /addgroup <group_id>"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "back_main":
        user = query.from_user
        data = load_data()
        
        keyboard = [
            [InlineKeyboardButton("📋 Features", callback_data="features")],
            [InlineKeyboardButton("📞 Admin ဆက်သွယ်ရန်", url=f"https://t.me/{ADMIN_USERNAME}")],
        ]
        if str(user.id) in data.get("approved", []):
            keyboard.insert(1, [InlineKeyboardButton("📤 Forward Post", callback_data="forward_guide")])
            keyboard.insert(2, [InlineKeyboardButton("📂 My Groups", callback_data="my_groups")])
        
        welcome_text = (
            "🚀 𝗔𝘂𝘁𝗼 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗕𝗼𝘁\n\n"
            "ကိုယ့် Channel post တွေကို Group တွေထဲ\n"
            "Auto Share ပေးတဲ့ Bot ဖြစ်ပါတယ်။\n\n"
            "✅ Features ကြည့်ရန် အောက်က button နှိပ်ပါ။"
        )
        await query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

# Handle forwarded messages from approved users
async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    
    # Check if user is approved
    if str(user.id) not in data.get("approved", []):
        await update.message.reply_text("❌ သုံးခွင့် မရှိသေးပါ။ Admin ကို ဆက်သွယ်ပါ။")
        return
    
    # Get user's groups (default + custom)
    default_groups = load_default_groups()
    assigned_defaults = default_groups[:3]
    custom_groups = data.get("user_groups", {}).get(str(user.id), [])
    
    all_groups = assigned_defaults + custom_groups
    
    if not all_groups:
        await update.message.reply_text("❌ Group မရှိသေးပါ။ Admin ကို ဆက်သွယ်ပါ။")
        return
    
    # Forward to all groups
    success = 0
    failed = 0
    failed_groups = []
    
    for group in all_groups:
        try:
            group_id = group.get("id")
            await context.bot.forward_message(
                chat_id=group_id,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )
            success += 1
        except Exception as e:
            failed += 1
            failed_groups.append(group.get("name", "Unknown"))
            logging.error(f"Forward failed to {group_id}: {e}")
    
    result_text = f"📤 Forward ပြီးပါပြီ!\n✅ Success: {success}\n❌ Failed: {failed}"
    if failed_groups:
        result_text += f"\n\nBan/Error Groups:\n" + "\n".join(f"- {g}" for g in failed_groups)
        result_text += "\n\nAdmin ကို ဆက်သွယ်ပြီး Group အသစ် ပြောင်းပါ။"
    
    await update.message.reply_text(result_text)

# Admin commands
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /approve <user_id>")
        return
    
    user_id = context.args[0]
    data = load_data()
    
    if user_id not in data.get("approved", []):
        if "approved" not in data:
            data["approved"] = []
        data["approved"].append(user_id)
        save_data(data)
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text="✅ Approve ပြီးပါပြီ! Bot သုံးလို့ ရပါပြီ။\n/start နှိပ်ပြီး စတင်ပါ။"
            )
        except:
            pass
        
        await update.message.reply_text(f"✅ User {user_id} approved!")
    else:
        await update.message.reply_text("User already approved.")

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /reject <user_id>")
        return
    
    user_id = context.args[0]
    data = load_data()
    
    if user_id in data.get("approved", []):
        data["approved"].remove(user_id)
        save_data(data)
    
    await update.message.reply_text(f"❌ User {user_id} rejected/removed.")

async def adddefault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin adds a default group: /adddefault <group_id> <group_name>"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /adddefault <group_id> <group_name>")
        return
    
    group_id = context.args[0]
    group_name = " ".join(context.args[1:])
    
    groups = load_default_groups()
    groups.append({"id": group_id, "name": group_name, "active": True})
    save_default_groups(groups)
    
    await update.message.reply_text(f"✅ Default group added: {group_name}\nTotal: {len(groups)}")

async def removedefault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin removes a default group: /removedefault <index>"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /removedefault <index (1-based)>")
        return
    
    idx = int(context.args[0]) - 1
    groups = load_default_groups()
    
    if 0 <= idx < len(groups):
        removed = groups.pop(idx)
        save_default_groups(groups)
        await update.message.reply_text(f"✅ Removed: {removed['name']}\nTotal: {len(groups)}")
    else:
        await update.message.reply_text("❌ Invalid index.")

async def listdefault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin lists all default groups"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    groups = load_default_groups()
    if not groups:
        await update.message.reply_text("No default groups yet. Use /adddefault <group_id> <name>")
        return
    
    text = "📂 Default Groups:\n\n"
    for i, g in enumerate(groups, 1):
        status = "✅" if g.get("active") else "❌"
        text += f"{i}. {status} {g['name']} ({g['id']})\n"
    text += f"\nTotal: {len(groups)}"
    
    await update.message.reply_text(text)

async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User adds custom group: /addgroup <group_id> <group_name>"""
    user = update.effective_user
    data = load_data()
    
    if str(user.id) not in data.get("approved", []):
        await update.message.reply_text("❌ သုံးခွင့် မရှိသေးပါ။")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addgroup <group_id> <group_name>")
        return
    
    group_id = context.args[0]
    group_name = " ".join(context.args[1:])
    
    if "user_groups" not in data:
        data["user_groups"] = {}
    if str(user.id) not in data["user_groups"]:
        data["user_groups"][str(user.id)] = []
    
    data["user_groups"][str(user.id)].append({"id": group_id, "name": group_name})
    save_data(data)
    
    await update.message.reply_text(f"✅ Group added: {group_name}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin stats"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    data = load_data()
    total_users = len(data.get("users", {}))
    approved = len(data.get("approved", []))
    groups = load_default_groups()
    
    text = (
        f"📊 𝗦𝘁𝗮𝘁𝘀\n\n"
        f"👥 Total Users: {total_users}\n"
        f"✅ Approved: {approved}\n"
        f"📂 Default Groups: {len(groups)}"
    )
    await update.message.reply_text(text)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # User commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addgroup", addgroup))
    
    # Admin commands
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("reject", reject))
    app.add_handler(CommandHandler("adddefault", adddefault))
    app.add_handler(CommandHandler("removedefault", removedefault))
    app.add_handler(CommandHandler("listdefault", listdefault))
    app.add_handler(CommandHandler("stats", stats))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Handle forwarded messages
    app.add_handler(MessageHandler(filters.FORWARDED & ~filters.COMMAND, handle_forward))
    
    print("Auto Forward Bot is running...")
    app.run_polling()
