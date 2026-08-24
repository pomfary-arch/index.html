import os
from pyrogram import Client, filters
import yt_dlp

# بياناتك الشخصية المعتمدة للبوت
API_ID = 27040406
API_HASH = "e1655170342494389f8e634ae2913d05"
BOT_TOKEN = "8820185149:AAFPwPClb0Do_zSGRLwoUaxHnBmw5hTREDM"
OWNER_ID = 7354941749  # آي دي حسابك الشخصي للحماية المطلقة (@rs7tx)

app = Client(
    "UltimatePersonalBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# فلتر حماية: البوت لا يستجيب إلا لك وحدك
owner_filter = filters.user(OWNER_ID)

@app.on_message(filters.command("start") & owner_filter)
async def start_command(client, message):
    await message.reply_text(
        "**أهلاً بك يا فري (علي جاسم) في بوتك الشخصي الخارق! 🚀**\n\n"
        "النواة الأساسية تعمل الآن بكفاءة مطلقة.\n"
        "أرسل لي أي رابط وسائط (تيك توك، إنستغرام، فيسبوك، يوتيوب، سناب...) وسأقوم بتحميله فوراً."
    )

@app.on_message(filters.regex(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+") & owner_filter)
async def handle_media_download(client, message):
    url = message.text.strip()
    status_msg = await message.reply_text("⏳ **جاري تحليل الرابط والتحميل... انتظر قليلاً**")

    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'format': 'best',
        'noplaylist': True,
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("📤 **جاري رفع الملف إلى تليجرام...**")

        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            await message.reply_photo(filename)
        elif filename.lower().endswith(('.mp3', '.m4a', '.wav', '.flac')):
            await message.reply_audio(filename)
        else:
            await message.reply_video(filename, supports_streaming=True)

        await status_msg.delete()
        
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status_msg.edit_text(f"❌ **حدث خطأ أثناء التحميل:**\n`{str(e)}`")

if __name__ == "__main__":
    print("🤖 جاري تشغيل البوت الشخصي...")
    app.run()
    
