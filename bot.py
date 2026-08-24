import os
import re
import shutil
import uuid
import glob
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, InputMediaPhoto
import yt_dlp
import subprocess

# ==========================================
# 🔑 بيانات البوت الأساسية
API_ID = 29630985
API_HASH = "80f83737b46944e8bc9e7355fa989dfb"
BOT_TOKEN = "7759556272:AAG23J5UfD3fD9v-5o7c1y3z9Xy4v2m1n0A"
# ==========================================

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text(
        "أهلاً بك يا علي جاسم في بوت التحميل الشامل الخارق! 🚀🔥\n\n"
        "أرسل لي أي رابط (فيديو أو صور من تيك توك، إنستغرام، يوتيوب...) وسأقوم بتحميله فوراً."
    )

@app.on_message(filters.text & filters.regex(r"https?://[^\s]+"))
def handle_link(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 تحميل فيديو / 🖼 صور", callback_data="dl_media")],
        [InlineKeyboardButton("🎵 استخراج الصوت (MP3)", callback_data="dl_audio")]
    ])
    message.reply_text("تم لقط الرابط بنجاح! اختر ماذا تريد استخراجه 👇", reply_markup=keyboard, reply_to_message_id=message.id)

@app.on_callback_query()
def handle_callback(client, callback_query):
    msg = callback_query.message
    
    try:
        url = re.search(r"https?://[^\s]+", msg.reply_to_message.text).group(0)
    except:
        msg.edit_text("❌ عذراً، لم أتمكن من العثور على الرابط الأصلي.")
        return

    mode = "media" if callback_query.data == "dl_media" else "audio"
    msg.edit_text("⏳ جاري التحميل والمعالجة (سواء صور أو فيديوهات)، يرجى الانتظار...")
    
    task_id = str(uuid.uuid4())
    download_dir = f"downloads/{task_id}"
    os.makedirs(download_dir, exist_ok=True)

    try:
        # محاولة التحميل باستخدام yt-dlp أولاً (للفيديوهات والصوتيات)
        if mode == "audio":
            ydl_opts = {
                'outtmpl': f"{download_dir}/%(title)s.%(ext)s",
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        else:
            ydl_opts = {
                'outtmpl': f"{download_dir}/%(title)s.%(ext)s",
                'format': 'bestvideo+bestaudio/best/best',
                'quiet': True,
                'noplaylist': False
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception:
                # إذا فشل yt-dlp (لأن الرابط صور وليس فيديو)، نقوم بتحميله تلقائياً عبر gallery-dl
                subprocess.run(["gallery-dl", "--dest", download_dir, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # جمع الملفات المحملة
        files = glob.glob(f"{download_dir}/**/*", recursive=True) + glob.glob(f"{download_dir}/*")
        files = list(set([f for f in files if os.path.isfile(f)]))
        
        if not files:
            msg.edit_text("❌ لم يتم العثور على ملفات. تأكد أن الرابط عام وليس لحساب خاص.")
            return

        media_group = []
        audio_files = []
        
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in ['mp4', 'mkv', 'webm', 'mov', 'm4v']:
                media_group.append(InputMediaVideo(file))
            elif ext in ['jpg', 'jpeg', 'png', 'webp', 'jfif']:
                media_group.append(InputMediaPhoto(file))
            elif ext in ['mp3', 'm4a', 'wav', 'aac', 'opus']:
                audio_files.append(file)

        if mode == "audio" or audio_files:
            for audio in audio_files:
                client.send_audio(msg.chat.id, audio, caption="🎵 تم استخراج الصوت بنجاح!")
            msg.delete()
            
        elif len(media_group) == 1:
            item = media_group[0]
            if isinstance(item, InputMediaVideo):
                client.send_video(msg.chat.id, item.media, caption="🎬 تفضل الفيديو الخاص بك!")
            elif isinstance(item, InputMediaPhoto):
                client.send_photo(msg.chat.id, item.media, caption="🖼 تفضل الصورة الخاصة بك!")
            msg.delete()
            
        elif len(media_group) > 1:
            for i in range(0, len(media_group), 10):
                client.send_media_group(msg.chat.id, media_group[i:i+10])
            client.send_message(msg.chat.id, "✅ تم تنزيل ألبوم الصور/الفيديوهات بالكامل!", reply_to_message_id=msg.reply_to_message.id)
            msg.delete()
            
        else:
            msg.edit_text("❌ الملفات المحملة بصيغة غير مدعومة.")
            
    except Exception as e:
        msg.edit_text(f"❌ حدث خطأ أثناء المعالجة. تأكد أن الرابط صحيح وعام.")
    finally:
        shutil.rmtree(download_dir, ignore_errors=True)

app.run()
        
