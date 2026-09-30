"""
SkillUp Bot — принимает заявки с лендинга через Webhook и выдаёт бесплатный урок
Демонстрационный проект для портфолио.
Зависимости: pip install aiogram aiohttp
"""
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ЗАМЕНИТЕ НА ВАШИ ДАННЫЕ
BOT_TOKEN = "YOUR_TOKEN_HERE"
ADMIN_ID = 123456789

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

COURSES = [
    ("🐍 Python-разработчик", "python"),
    ("🎨 UX/UI Дизайнер", "design"),
    ("📈 Интернет-маркетолог", "marketing"),
]

@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"course_{key}")]
        for name, key in COURSES
    ])
    await msg.answer(
        "🎓 <b>SkillUp — подберём курс!</b>\n\nВыберите направление, и я пришлю бесплатный вводный урок:",
        parse_mode="HTML", reply_markup=kb
    )

@dp.callback_query(F.data.startswith("course_"))
async def course(c: types.CallbackQuery):
    key = c.data.split("_")[1]
    lessons = {
        "python": "🐍 <b>Урок 1:</b> Переменные и типы данных в Python\n\n[Смотреть видео](https://example.com/python)\n\nПонравилось? Запишитесь на полный курс!",
        "design": "🎨 <b>Урок 1:</b> Основы композиции и сетки в Figma\n\n[Смотреть видео](https://example.com/design)\n\nХотите продолжить?",
        "marketing": "📈 <b>Урок 1:</b> Как настроить первый таргет VK\n\n[Смотреть видео](https://example.com/marketing)\n\nГотовы к полному курсу?",
    }
    await c.message.answer(
        lessons.get(key, "Урок в процессе записи"), 
        parse_mode="HTML", 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Записаться на полный курс", url="https://skillup.example.com")],
            [InlineKeyboardButton(text="💬 Задать вопрос менеджеру", url="https://t.me/skillup_manager")],
        ])
    )
    await bot.send_message(ADMIN_ID, f"🎓 @{c.from_user.username} выбрал курс: {key}")

# ── Webhook обработчик для приёма заявок с лендинга ──
async def webhook_handler(request):
    try:
        data = await request.json()
        name = data.get('name', 'Не указано')
        phone = data.get('phone', 'Не указано')
        
        await bot.send_message(
            ADMIN_ID,
            f"🔔 <b>Новая заявка с лендинга!</b>\n\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"🌐 Источник: {data.get('source', 'site')}",
            parse_mode="HTML"
        )
        return web.Response(text="OK", status=200)
    except Exception as e:
        return web.Response(text=f"Error: {e}", status=500)

async def main():
    # Запуск веб-сервера для приёма webhook-ов с сайта
    app = web.Application()
    app.router.add_post('/webhook/skillup', webhook_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Webhook сервер запущен на порту 8080")
    
    # Запуск бота
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
