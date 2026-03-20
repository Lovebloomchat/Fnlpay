import os
import asyncio
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from playwright.async_api import async_playwright

TOKEN = os.getenv("BOT_TOKEN")


async def process_numbers(numbers):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://retailerportal.paynearby.in/auth/login")

        # 🔥 STEP 1: first login attempt (IMPORTANT)
        await page.fill('input[placeholder="Mobile number"]', "9983027190")
        await page.fill('input[placeholder="Password"]', "Shubham@9228")
        await page.click('button[type="submit"]')

        await asyncio.sleep(5)  # wait for system ready

        # 🔥 STEP 2: now loop (NO REFRESH)
        for num in numbers:
            num = num.strip()

            try:
                # clear + type new number
                await page.fill('input[placeholder="Mobile number"]', "")
                await page.fill('input[placeholder="Mobile number"]', num)

                await asyncio.sleep(2)

                content = await page.content()

                if "not registered with us" in content.lower():
                    results.append(f"{num} : NOT REGISTERED")
                else:
                    results.append(f"{num} : REGISTERED")

            except:
                results.append(f"{num} : ERROR")

        await browser.close()

    return results


def start(update: Update, context: CallbackContext):
    update.message.reply_text("📂 Send .txt file with numbers")


def handle_file(update: Update, context: CallbackContext):
    file = update.message.document

    if not file.file_name.endswith(".txt"):
        update.message.reply_text("❌ Send only .txt file")
        return

    update.message.reply_text("⏳ Processing started...")

    file_path = "input.txt"
    output_path = "output.txt"

    file.get_file().download(file_path)

    with open(file_path, "r") as f:
        numbers = f.read().splitlines()

    results = asyncio.run(process_numbers(numbers))

    with open(output_path, "w") as f:
        f.write("\n".join(results))

    update.message.reply_document(document=open(output_path, "rb"))


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_file))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
