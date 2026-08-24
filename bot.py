import os
import re
import shutil
import uuid
import glob
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, InputMediaPhoto
import yt_dlp

# ==========================================
# 🔑 تم وضع بياناتك وجهوزية التوكن بالكامل هنا
API_ID = 29630985
API_HASH = "80f83737b46944e8bc9e7355fa989dfb"
BOT_TOKEN = "7759556272:AAG23J5UfD3fD9v-5o7c1y3z9Xy4v2m1n0A"
# ==========================================

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_ydl_options(task_id, mode="video"):
    options = {
        'outtmpl': f"downloads/{task_id}/%(title)s.%(ext)s",
        'quiet': True,
        'no_warnings': True,
        'noplaylist': False,
    }
    
    if mode == "audio":
        options['format'] = 'bestaudio/best'
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        options['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        
    return options

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("أهلاً بك يا علي جاسم في بوتك الشامل! 🚀\n\nأرسل لي أي رابط (تيك توك، إنستغرام، يوتيوب، الخ...) وسأعطيك خيارات تحميل الفيديو، الصور، أو استخراج الصوت.")

@app.on_message(filters.text & filters.regex(r"https?://[^\s]+"))
def handle_link(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 تحميل فيديو / 🖼 صور", callback_data="dl_media")],
        [InlineKeyboardButton("🎵 استخراج الصوت (MP3)", callback_data="dl_audio")]
    ])
    message.reply_text("لقطت الرابط! شنو تحب أنزل لك؟ 👇", reply_markup=keyboard, reply_to_message_id=message.id)

@app.on_callback_query()
def handle_callback(client, callback_query):
    msg = callback_query.message
    
    try:
        url = re.search(r"https?://[^\s]+", msg.reply_to_message.text).group(0)
    except:
        msg.edit_text("❌ لم أتمكن من العثور على الرابط الأصلي.")
        return

    mode = "media" if callback_query.data == "dl_media" else "audio"
    msg.edit_text("⏳ جاري التحميل والمعالجة، انتظر ثواني...")
    
    task_id = str(uuid.uuid4())
    os.makedirs(f"downloads/{task_id}", exist_ok=True)
    opts = get_ydl_options(task_id, mode)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        files = glob.glob(f"downloads/{task_id}/*")
        
        if not files:
            msg.edit_text("❌ حدث خطأ، إما أن الرابط خاص (Private) أو غير مدعوم.")
            return

        media_group = []
        audio_files = []
        
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in ['mp4', 'mkv', 'webm']:
                media_group.append(InputMediaVideo(file))
            elif ext in ['jpg', 'jpeg', 'png', 'webp']:
                media_group.append(InputMediaPhoto(file))
            elif ext in ['mp3', 'm4a', 'wav']:
                audio_files.append(file)

        if mode == "audio" or audio_files:
            for audio in audio_files:
                client.send_audio(msg.chat.id, audio, caption="🎵 تم استخراج الصوت بواسطة بوتك!")
            msg.delete()
            
        elif len(media_group) == 1:
            item = media_group[0]
            if isinstance(item, InputMediaVideo):
                client.send_video(msg.chat.id, item.media, caption="🎬 تفضل الفيديو!")
            elif isinstance(item, InputMediaPhoto):
                client.send_photo(msg.chat.id, item.media, caption="🖼 تفضل الصورة!")
            msg.delete()
            
        elif len(media_group) > 1:
            for i in range(0, len(media_group), 10):
                client.send_media_group(msg.chat.id, media_group[i:i+10])
            client.send_message(msg.chat.id, "✅ تم تحميل الألبوم بالكامل!", reply_to_message_id=msg.reply_to_message.id)
            msg.delete()
            
        else:
            msg.edit_text("❌ تم التحميل ولكن بصيغة غير مدعومة للعرض المباشر.")
            
    except Exception as e:
        msg.edit_text(f"❌ حدث خطأ أثناء التحميل، تأكد أن المنشور ليس خاصاً.")
    finally:
        shutil.rmtree(f"downloads/{task_id}", ignore_errors=True)

app.run()
                                  
