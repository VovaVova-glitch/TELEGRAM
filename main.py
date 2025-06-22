from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)

import os

TOKEN = os.getenv("BOT_TOKEN")  # Обязательно установи переменную окружения BOT_TOKEN на Render

# Состояния
GOAL, GENDER, AGE, HEIGHT, WEIGHT, ACTIVITY, TRAINING, GOAL_MEAL = range(8)
DAYS_HOME, TIME_HOME, EQUIP_HOME, GOAL_HOME = range(100, 104)
DAYS_GYM, TIME_GYM, EXPERIENCE_GYM, GOAL_GYM = range(200, 204)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я твой фитнес-бот 💪\n"
        "Я помогу тебе с КБЖУ, тренировками и питанием!\n\n"
        "Команды:\n"
        "/kcal — расчёт КБЖУ\n"
        "/meal — рацион на день\n"
        "/meal_week — рацион на неделю\n"
        "/workout_home — тренировки дома\n"
        "/workout_gym — тренировки в зале\n"
        "/cancel — отмена"
    )

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# КБЖУ
async def start_kcal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    reply_keyboard = [['похудеть', 'набрать', 'поддерживать вес']]
    await update.message.reply_text("🧮 1️⃣ Какая твоя цель?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return GOAL

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal'] = update.message.text.lower()
    reply_keyboard = [['м', 'ж']]
    await update.message.reply_text("2️⃣ Укажи свой пол:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['gender'] = update.message.text.lower()
    await update.message.reply_text("3️⃣ Сколько тебе лет?", reply_markup=ReplyKeyboardRemove())
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = int(update.message.text)
    await update.message.reply_text("4️⃣ Укажи рост (см):")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['height'] = int(update.message.text)
    await update.message.reply_text("5️⃣ Укажи вес (кг):")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['weight'] = int(update.message.text)
    reply_keyboard = [['низкий', 'средний', 'высокий']]
    await update.message.reply_text("6️⃣ Уровень активности:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return ACTIVITY

async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['activity'] = update.message.text.lower()
    reply_keyboard = [['дом', 'зал', 'не тренируюсь']]
    await update.message.reply_text("7️⃣ Где тренируешься?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return TRAINING

async def training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    d['training'] = update.message.text.lower()
    bmr = 10 * d["weight"] + 6.25 * d["height"] - 5 * d["age"] + (5 if d["gender"] == "м" else -161)
    factor = {"низкий": 1.2, "средний": 1.5, "высокий": 1.75}.get(d["activity"], 1.2)
    bmr *= factor
    if d["goal"] == "похудеть": bmr -= 300
    elif d["goal"] == "набрать": bmr += 300
    kcal = round(bmr)
    protein = round(d["weight"] * 2)
    fat = round(d["weight"] * 1)
    carbs = round((kcal - (protein * 4 + fat * 9)) / 4)
    await update.message.reply_text(
        f"✅ КБЖУ:\n🔸 Калории: {kcal} ккал\n🔸 Белки: {protein} г\n🔸 Жиры: {fat} г\n🔸 Углеводы: {carbs} г",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# /meal
async def meal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    reply_keyboard = [['похудеть', 'набрать', 'поддерживать']]
    await update.message.reply_text("🍽 Какая цель питания?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return GOAL_MEAL

async def meal_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    if goal == "похудеть":
        text = "🍏 Завтрак: овсянка + яйцо\nОбед: курица + гречка\nУжин: творог + овощи\n🔻 1600–1800 ккал"
    elif goal == "набрать":
        text = "💪 Завтрак: овсянка + банан\nОбед: рис + говядина\nУжин: омлет + хлеб\n🔺 2800–3200 ккал"
    else:
        text = "⚖️ Завтрак: яйца + хлеб\nОбед: курица + рис\nУжин: рыба + овощи\n🔸 2000–2200 ккал"
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# === Создание и запуск бота ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("kcal", start_kcal)],
        states={
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, goal)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activity)],
            TRAINING: [MessageHandler(filters.TEXT & ~filters.COMMAND, training)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("meal", meal)],
        states={GOAL_MEAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, meal_result)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.run_polling()

if __name__ == '__main__':
    main()
