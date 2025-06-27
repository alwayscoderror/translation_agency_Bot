import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MANAGER_ID = int(os.getenv("MANAGER_ID"))

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Данные по услугам и ценам
SERVICES = {
    "passport": {
        "name": "Паспорт",
        "name_cn": "护照",
        "desc": "Перевод паспорта с нотариальным заверением.",
        "desc_cn": "护照翻译及公证。",
        "prices": {
            "en": 1200,
            "zh": 1500
        }
    },
    "diploma": {
        "name": "Диплом",
        "name_cn": "毕业证书",
        "desc": "Перевод диплома с нотариальным заверением.",
        "desc_cn": "毕业证书翻译及公证。",
        "prices": {
            "en": 2700,
            "zh": 3000
        }
    },
    "attestat": {
        "name": "Аттестат",
        "name_cn": "中学毕业证书",
        "desc": "Перевод аттестата с нотариальным заверением.",
        "desc_cn": "中学毕业证书翻译及公证。",
        "prices": {
            "en": 1500,
            "zh": 1800
        }
    },
    "driver": {
        "name": "Водительское удостоверение",
        "name_cn": "驾驶证",
        "desc": "Перевод водительского удостоверения с нотариальным заверением.",
        "desc_cn": "驾驶证翻译及公证。",
        "prices": {
            "en": 2200,
            "zh": 2500
        }
    },
    "textdoc": {
        "name": "Текстовый документ (цена за 1 стр.)",
        "name_cn": "文本文件（价格按页计算）",
        "desc": "Перевод текстового документа (цена за 1 страницу).",
        "desc_cn": "文本文件翻译。价格按页计算。",
        "prices": {
            "en": 600,
            "zh": 900
        }
    },
    "contract": {
        "name": "Договор + приложение к договору",
        "name_cn": "合同及附件",
        "desc": "Перевод договора и приложения",
        "desc_cn": "合同和附件的翻译",
        "prices": {
            "en": 4700,
            "zh": 5000
        }
    },
    "business_license": {
        "name": "Бизнес-лицензия",
        "name_cn": "营业执照",
        "desc": "Перевод бизнес-лицензии с нотариальным заверением.",
        "desc_cn": "营业执照翻译及公证。",
        "prices": {
            "en": 4200,
            "zh": 4500
        }
    },
    "study_cert": {
        "name": "Справка об обучении",
        "name_cn": "在读证明",
        "desc": "Перевод справки об обучении.",
        "desc_cn": "在读证明翻译。",
        "prices": {
            "en": 1500,
            "zh": 1800
        }
    },
    "grade_report": {
        "name": "Табель успеваемости",
        "name_cn": "成绩单",
        "desc": "Перевод табеля успеваемости.",
        "desc_cn": "成绩单翻译。",
        "prices": {
            "en": 2200,
            "zh": 2500
        }
    },
    "degree_confirm": {
        "name": "Подтверждение о наличии ученой степени",
        "name_cn": "学位证明",
        "desc": "Перевод подтверждения о наличии ученой степени.",
        "desc_cn": "学位证明翻译。",
        "prices": {
            "en": 1500,
            "zh": 1800
        }
    }
}
LANGS = {"en": "🇬🇧 Английский ⇄ Русский 🇷🇺", "zh": "🇨🇳 Китайский ⇄ Русский 🇷🇺"}
LANGS_CN = {"en": "英俄互译", "zh": "中俄互译"}
LANGS_SHORT = {"en": "🇬🇧 ⇄ 🇷🇺", "zh": "🇨🇳 ⇄ 🇷🇺"}

# Двуязычные подписи
RU = {
    "main_menu": "Главное меню",
    "welcome": "Добро пожаловать в чат-бота Бюро Переводов!",
    "help": "Я помогу вам узнать об услугах, их стоимости, а также оставить заявку.",
    "services": "Услуги",
    "recent": "Недавно просмотренные:",
    "contact": "Хочу перевод!",
    "back": "Назад",
    "all_services": "Все услуги",
    "to_channel": "Вернуться в канал",
    "send_phone": "Отправить номер телефона",
    "cancel": "Отмена",
    "choose_lang": "Выберите языковую пару:",
    "choose_service": "Выберите услугу по переводу:",
    "price": "Стоимость",
    "days": "Срок: 1–2 рабочих дня",
    "min_order": "Минимальный заказ — 1 стр. (1800 знаков с пробелами)",
    "thank_you": "Спасибо! Ваши данные отправлены менеджеру. Мы свяжемся с вами в ближайшее время.",
    "choose_action": "Выберите действие:",
    "send_phone_info": "Пожалуйста, отправьте ваш номер телефона, нажав на кнопку ниже или напишите его вручную.",
}
CN = {
    "main_menu": "主菜单",
    "welcome": "欢迎来到翻译局机器人！",
    "help": "我可以帮您了解服务、价格，也可以提交申请。",
    "services": "服务",
    "recent": "最近浏览：",
    "contact": "我要翻译！",
    "back": "返回",
    "all_services": "所有服务",
    "to_channel": "返回频道",
    "send_phone": "发送电话号码",
    "cancel": "取消",
    "choose_lang": "请选择语种：",
    "choose_service": "请选择翻译服务：",
    "price": "价格",
    "days": "时长：1-2个工作日",
    "min_order": "最小订单 — 1页（含空格1800字符）",
    "thank_you": "谢谢！您的信息已发送给经理。我们会尽快与您联系。",
    "choose_action": "请选择操作：",
    "send_phone_info": "请点击下方按钮发送您的电话号码，或手动输入。",
}

def get_main_menu(context=None):
    rows = [
        [InlineKeyboardButton(f"📋 {RU['services']} / {CN['services']}", callback_data="services")],
        [InlineKeyboardButton(f"💬 {RU['contact']} / {CN['contact']}", callback_data="contact")],
        [InlineKeyboardButton(f"🏠 {RU['to_channel']} / {CN['to_channel']}", url="https://t.me/fanyibumen")]
    ]
    # Добавляем кнопку очистки истории, если она есть
    if context and context.user_data.get("history"):
        rows.append([InlineKeyboardButton("🧹 Очистить историю / 清除浏览记录", callback_data="clear_history")])
    return InlineKeyboardMarkup(rows)

def get_services_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{SERVICES[svc]['name']} / {SERVICES[svc]['name_cn']}", callback_data=f"svc_{svc}")] for svc in SERVICES] +
        [[InlineKeyboardButton(f"↩️ {RU['back']} / {CN['back']}", callback_data="back_main")]]
    )

def get_service_lang_menu(service_key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{LANGS[lang]} / {LANGS_CN[lang]}", callback_data=f"svc_{service_key}_lang_{lang}")] for lang in SERVICES[service_key]["prices"]] +
        [[InlineKeyboardButton(f"↩️ {RU['back']} / {CN['back']}", callback_data="services")]]
    )

def get_price_menu(service_key, lang):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"↩️ {RU['back']} / {CN['back']}", callback_data=f"svc_{service_key}"),
            InlineKeyboardButton(f"📋 {RU['all_services']} / {CN['all_services']}", callback_data="services")
        ],
        [InlineKeyboardButton(f"🏠 {RU['main_menu']} / {CN['main_menu']}", callback_data="back_main")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu = get_main_menu(context)
    # Формируем историю
    history_text = ""
    history = context.user_data.get("history", [])
    if history:
        history_text += f"\n\n<b>{RU['recent']}</b>\n<b>{CN['recent']}</b>"
        for item in history:
            if isinstance(item, tuple) and len(item) == 2:
                svc_key, lang_key = item
                svc = SERVICES[svc_key]
                flag = LANGS_SHORT[lang_key]
                price = svc["prices"][lang_key]
                history_text += (
                    f"\n• {svc['name']} {svc['name_cn']}（{flag}）：<b>{price}₽</b>"
                )
    welcome_text = (
        f"{RU['welcome']}\n{CN['welcome']}\n\n"
        f"{RU['help']}\n{CN['help']}"
        f"{history_text}"
    )
    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=menu,
            parse_mode="HTML"
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=menu,
            parse_mode="HTML"
        )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    await query.answer()

    # Главное меню
    if data == "services":
        await query.edit_message_text(
            f"{RU['choose_service']} / {CN['choose_service']}",
            reply_markup=get_services_menu()
        )
    elif data == "contact":
        await contact(update, context)
    elif data == "back_main":
        await start(update, context)
    elif data == "clear_history":
        context.user_data["history"] = []
        await query.edit_message_text(
            f"{RU['choose_action']}\n{CN['choose_action']}",
            reply_markup=get_main_menu(context)
        )
    # Услуга выбрана — показываем языковые пары
    elif data.startswith("svc_") and "_lang_" not in data:
        svc_key = data[4:]
        if svc_key in SERVICES:
            svc = SERVICES[svc_key]
            await query.edit_message_text(
                f"<b>{svc['name']}</b>\n{svc['desc']}\n\n{svc['desc_cn']}\n\n{RU['choose_lang']} / {CN['choose_lang']}:",
                reply_markup=get_service_lang_menu(svc_key),
                parse_mode="HTML"
            )
        else:
            await query.edit_message_text(
                "Услуга не найдена. Пожалуйста, выберите из меню ещё раз.",
                reply_markup=get_services_menu()
            )
    # Языковая пара выбрана — показываем цену и сроки
    elif "_lang_" in data:
        svc_key = data[4:data.rfind("_lang_")]
        lang = data[data.rfind("_lang_") + 6:]
        if svc_key in SERVICES:
            # Обновляем историю: сохраняем (svc_key, lang)
            history = context.user_data.get("history", [])
            pair = (svc_key, lang)
            if pair in history:
                history.remove(pair)
            history.insert(0, pair)
            context.user_data["history"] = history[:3]
            svc = SERVICES[svc_key]
            price = svc["prices"][lang]
            text = (
                f"📄 <b>{svc['name']} / {svc['name_cn']}</b>\n{LANGS[lang]} / {LANGS_CN[lang]}\n\n"
                f"{RU['price']} {CN['price']}：<b>{price} ₽</b>\n"
                f"{RU['days']}\n{CN['days']}"
            )
            await query.edit_message_text(
                text,
                reply_markup=get_price_menu(svc_key, lang),
                parse_mode="HTML"
            )
        else:
            await query.edit_message_text(
                "Услуга не найдена. Пожалуйста, выберите из меню ещё раз.",
                reply_markup=get_services_menu()
            )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton(f"📱 {RU['send_phone']} / {CN['send_phone']}", request_contact=True)],
        [KeyboardButton(f"❌ {RU['cancel']} / {CN['cancel']}")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    info_text = f"{RU['send_phone_info']}\n{CN['send_phone_info']}"
    if update.callback_query:
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        await update.callback_query.message.reply_text(
            info_text,
            reply_markup=reply_markup
        )
    elif update.message:
        await update.message.reply_text(
            info_text,
            reply_markup=reply_markup
        )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.message.from_user
    text = (
        f"Новая заявка!\n"
        f"Имя: {user.full_name}\n"
        f"Телефон: {contact.phone_number}\n"
        f"Username: @{user.username if user.username else '-'}\n"
        f"User ID: {user.id}"
    )
    await context.bot.send_message(chat_id=MANAGER_ID, text=text)
    # Сначала благодарность и скрытие клавиатуры
    await update.message.reply_text(
        f"{RU['thank_you']}\n{CN['thank_you']}",
        reply_markup=ReplyKeyboardRemove()
    )
    # Затем главное меню
    await update.message.reply_text(
        f"{RU['choose_action']}\n{CN['choose_action']}",
        reply_markup=get_main_menu(context)
    )

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{RU['choose_action']}\n{CN['choose_action']}",
        reply_markup=get_main_menu(context)
    )

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(CommandHandler("contact", contact))
    application.add_handler(
        MessageHandler(filters.CONTACT, handle_contact)
    )
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r'^❌'), handle_cancel)
    )
    application.run_polling()

if __name__ == "__main__":
    main() 