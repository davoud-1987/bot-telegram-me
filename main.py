

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3
import requests

# =====================
# تنظیمات
# =====================
API_TOKEN = "7136725278:AAEW4DZ6tanqCjj5KCOiPHIZ6jjcB6YEVos"
MERCHANT_ID = "کد_مرچنت_زرین_پال"   # از پنل زرین‌پال می‌گیری
CALLBACK_URL = "https://yourdomain.com/verify"  # آدرس سرور برای بازگشت از پرداخت

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# =====================
# دیتابیس
# =====================
conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# جدول پروفایل کاربران
cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT
)
""")

# جدول سفارش‌ها
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product TEXT,
    quantity INTEGER,
    amount INTEGER,
    paid INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES profiles (user_id)
)
""")

conn.commit()
conn.close()

# =====================
# متغیرهای موقت
# =====================
user_data = {}
orders_data = {}

# =====================
# ثبت پروفایل
# =====================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("سلام 👋 لطفاً اسم خودتو وارد کن:")
    user_data[message.from_user.id] = {}

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "name" not in user_data[msg.from_user.id])
async def get_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    await message.reply("📱 شماره موبایل رو وارد کن:")

@dp.message_handler(lambda msg: "phone" not in user_data.get(msg.from_user.id, {}))
async def get_phone(message: types.Message):
    user_data[message.from_user.id]["phone"] = message.text
    await message.reply("✉ ایمیل رو وارد کن:")

@dp.message_handler(lambda msg: "email" not in user_data.get(msg.from_user.id, {}))
async def get_email(message: types.Message):
    user_data[message.from_user.id]["email"] = message.text
    await message.reply("🏠 آدرس رو وارد کن:")

@dp.message_handler(lambda msg: "address" not in user_data.get(msg.from_user.id, {}))
async def get_address(message: types.Message):
    user_data[message.from_user.id]["address"] = message.text
    data = user_data.pop(message.from_user.id)

    # ذخیره در دیتابیس
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO profiles (user_id, name, phone, email, address)
        VALUES (?, ?, ?, ?, ?)
    """, (message.from_user.id, data["name"], data["phone"], data["email"], data["address"]))
    conn.commit()
    conn.close()

    await message.reply("✅ پروفایل شما ذخیره شد!\nبرای دیدن پروفایل /profile رو بزن.")

# نمایش پروفایل
@dp.message_handler(commands=["profile"])
async def show_profile(message: types.Message):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone, email, address FROM profiles WHERE user_id = ?", (message.from_user.id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        await message.reply(f"📌 پروفایل شما:\n\n👤 نام: {row[0]}\n📱 موبایل: {row[1]}\n✉ ایمیل: {row[2]}\n🏠 آدرس: {row[3]}")
    else:
        await message.reply("❌ پروفایلی پیدا نشد. لطفاً با /start ثبت‌نام کنید.")

# =====================
# ثبت سفارش
# =====================
@dp.message_handler(commands=["order"])
async def start_order(message: types.Message):
    orders_data[message.from_user.id] = {}
    await message.reply("🛒 لطفاً نام محصول رو وارد کن:")

@dp.message_handler(lambda msg: msg.from_user.id in orders_data and "product" not in orders_data[msg.from_user.id])
async def get_product(message: types.Message):
    orders_data[message.from_user.id]["product"] = message.text
    await message.reply("📦 تعداد مورد نظر رو وارد کن:")

@dp.message_handler(lambda msg: msg.from_user.id in orders_data and "quantity" not in orders_data[msg.from_user.id])
async def get_quantity(message: types.Message):
    try:
        quantity = int(message.text)
    except ValueError:
        await message.reply("❌ لطفاً یک عدد معتبر وارد کن.")
        return

    product = orders_data[message.from_user.id]["product"]
    price_per_item = 10000  # قیمت نمونه، هر محصول 10,000 ریال
    amount = quantity * price_per_item

    orders_data[message.from_user.id]["quantity"] = quantity
    orders_data[message.from_user.id]["amount"] = amount

    # ذخیره در دیتابیس
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (user_id, product, quantity, amount) VALUES (?, ?, ?, ?)
    """, (message.from_user.id, product, quantity, amount))
    conn.commit()
    conn.close()

    # ارسال لینک پرداخت زرین‌پال
    result = create_payment_request(amount, f"سفارش {product}", "test@example.com", "09120000000")

    if "data" in result and "authority" in result["data"]:
        authority = result["data"]["authority"]
        payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
        await message.reply(
            f"✅ سفارش شما ثبت شد!\n\n"
            f"🛒 محصول: {product}\n"
            f"📦 تعداد: {quantity}\n"
            f"💰 مبلغ: {amount} ریال\n\n"
            f"برای پرداخت روی لینک زیر کلیک کنید:\n{payment_url}"
        )
    else:
        await message.reply("❌ خطا در اتصال به زرین‌پال. لطفاً دوباره تلاش کنید.")

# =====================
# تابع ایجاد درخواست پرداخت
# =====================
def create_payment_request(amount, description, email, mobile):
    url = "https://api.zarinpal.com/pg/v4/payment/request.json"
    data = {
        "merchant_id": MERCHANT_ID,
        "amount": amount,
        "description": description,
        "callback_url": CALLBACK_URL,
        "metadata": {"email": email, "mobile": mobile}
    }
    headers = {"accept": "application/json", "content-type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# =====================
# اجرای ربات
# =====================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
