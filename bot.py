import os
import re
import shutil
import uuid
import glob
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, InputMediaPhoto
import yt_dlp

# ==========================================
# 🔑 بيانات البوت الأساسية
API_ID = 27040406
API_HASH = "e1655170342494389f8e634ae2913d05"
BOT_TOKEN = "7759556272:AAG23J5UfD3fD9v-5o7c1y3z9Xy4v2m1n0A"
# ==========================================

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text(
        "أهلاً بك يا علي جاسم في بوت التحميل الشامل الخارق! 🚀🔥\n\n"
        "أرسل لي أي رابط (تيك توك، إنستغرام، يوتيوب...) وسأقوم بتحميله فوراً."
    )

@app.on_message(filters.text & filters.regex(r"https?://[^\s]+"))
def handle_link(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 تحميل الفيديو/الوسائط", callback_data="dl_media")],
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
    msg.edit_text("⏳ جاري التحميل والمعالجة، يرجى الانتظار...")
    
    task_id = str(uuid.uuid4())
    download_dir = f"downloads/{task_id}"
    os.makedirs(download_dir, exist_ok=True)

    try:
        ydl_opts = {
            'outtmpl': f"{download_dir}/%(id)s_%(title)s.%(ext)s",
            'quiet': True,
            'noplaylist': False,
            'fixup': 'detect_or_warn',
            'writethumbnail': False,
        }
        
        if mode == "audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # إعدادات تضمن جلب الوسائط بأعلى جودة وسحب الصور المرفقة
            ydl_opts['format'] = 'best/bestvideo+bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # البحث عن كافة الملفات المُحمّلة بشكل شامل داخل المجلد
        files = []
        for root, dirs, filenames in os.walk(download_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        
        files = list(set(files))
        
        if not files:
            msg.edit_text("❌ لم يتم العثور على ملفات. تأكد أن الرابط عام وليس لحساب خاص.")
            return

        media_group = []
        audio_files = []
        
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in ['mp4', 'mkv', 'webm', 'mov', 'm4v', 'avi']:
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
            # إرسال الصور والفيديوهات المتعددة كألبوم دفعة واحدة
            for i in range(0, len(media_group), 10):
                client.send_media_group(msg.chat.id, media_group[i:i+10])
            client.send_message(msg.chat.id, "✅ تم تنزيل جميع الملفات بنجاح!", reply_to_message_id=msg.reply_to_message.id)
            msg.delete()
            
        else:
            msg.edit_text("❌ الملفات المحملة بصيغة غير مدعومة.")
            
    except Exception as e:
        msg.edit_text(f"❌ حدث خطأ أثناء التحميل: {str(e)[:100]}")
    finally:
        shutil.rmtree(download_dir, ignore_errors=True)

app.run()
