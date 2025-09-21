import requests
from bs4 import BeautifulSoup
import os
import asyncio
from telethon import TelegramClient
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel = os.getenv("CHANNEL")
client = TelegramClient("session", api_id, api_hash)
async def send_files(file_path, caption):
    await client.send_file(channel, file_path, caption=caption)
    print(f"📤 تم إرسال الملف: {os.path.basename(file_path)}")

async def main():
    url = "https://latakia-univ.edu.sy/ar/Schedual/Results"
    department = [56, 69, 129, 130]
    index = 0

    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)

    # الملفات الموجودة مسبقاً بالفولدر (حتى اللي انزلت قبل تشغيل الكود)
    downloaded_files = set(os.listdir(download_folder))

    session = requests.Session()
    objects = set()
    while True:
        try:
            payload = {
                "facultyId": 51,
                "departmentId": department[index],
                "studyYearId": 12,
                "semesterId": 2
            }
            print("🔍 فحص الموقع...")

            response = session.post(url, data=payload)
            soup = BeautifulSoup(response.text, "html.parser")

            # بدّل القسم
            index = (index + 1) % len(department)

            # كل الروابط للـ PDF
            cards = soup.find_all("div", class_="item-content")
            for card in cards:
                caption = card.find("h3").text.strip()
                link = card.find("a")["href"]
                date = card.find("span").text.strip()

                file_url = link if link.startswith("http") else "https://latakia-univ.edu.sy" + link
                filename = os.path.basename(file_url)
                file_path = os.path.join(download_folder, filename)
                if caption in objects:
                    print("الملف مكرر")
                    continue
                else:
                    objects.add(caption)
                # ✅ إذا الملف موجود مسبقاً → تجاهلو
                if (filename in downloaded_files):
                    print(f"⚠️ {filename} موجود مسبقًا، تم التجاهل")
                    continue
                # 📥 نزّل الملف
                print(f"📥 ملف جديد: {filename} ... جاري التحميل")
                file_data = session.get(file_url)
                with open(file_path, "wb") as f:
                    f.write(file_data.content)

                downloaded_files.add(filename)
                print("✅ تم التحميل")

                # 📤 ابعت الملف الجديد
                await send_files(file_path, caption)
        except Exception as e:
            print(f"❌ خطأ: {e}")

        # ⏳ انتظر 3 ثانية
        await asyncio.sleep(3)

with client:
    client.loop.run_until_complete(main())
