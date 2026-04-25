import re
import asyncio
import requests
from urllib.parse import urlencode
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# ========== STORY-SAVE.COM (ПРИОРИТЕТНЫЙ) ==========
def get_video_storysave(instagram_url: str) -> dict | None:
    """Получает видео и статистику через story-save.com"""
    try:
        api_url = "https://story-save.com/content.php"
        full_url = f"{api_url}?{urlencode({'url': instagram_url})}"
        
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(full_url, headers=headers, timeout=15)
        data = response.json()
        
        if data.get('status') != 'ok':
            return None
        
        html = data.get('html', '')
        
        # Извлекаем username из HTML
        username = None
        username_match = re.search(r'<p class="mb-0 h4">([^<]+)</p>', html)
        if username_match:
            username = username_match.group(1).strip()
        
        # Извлекаем лайки
        likes = None
        likes_match = re.search(r'<i class="far fa-heart[^>]*></i>\s*([\d.]+[KM]?)', html, re.IGNORECASE)
        if likes_match:
            likes = likes_match.group(1)
        
        # Извлекаем комментарии
        comments = None
        comments_match = re.search(r'<i class="far fa-comment[^>]*></i>\s*([\d,]+)', html, re.IGNORECASE)
        if comments_match:
            comments = comments_match.group(1)
        
        # Ищем ссылку на скачивание
        match = re.search(r'href="([^"]*media\.php\?media=[^"]*)"', html)
        if match:
            media_url = match.group(1).replace('&amp;', '&')
            return {
                "media_url": media_url,
                "type": "video",
                "username": username,
                "likes": likes,
                "comments": comments
            }
        
        # Ищем прямую ссылку на .mp4
        mp4_match = re.search(r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)', html, re.IGNORECASE)
        if mp4_match:
            return {
                "media_url": mp4_match.group(1),
                "type": "video",
                "username": username,
                "likes": likes,
                "comments": comments
            }
            
    except Exception as e:
        logger.warning(f"Story-save ошибка: {e}")
    
    return None


# ========== ЗАПАСНЫЕ API ==========
API_LIST = [
    {
        "name": "nyanpasu64",
        "url": "https://api.nyanpasu64.com/instagram/download",
        "method": "GET",
        "params": lambda url: {"url": url},
        "parse": lambda data: _parse_nyanpasu(data)
    },
    {
        "name": "igdown",
        "url": "https://api.igdown.com/api/download",
        "method": "GET",
        "params": lambda url: {"url": url},
        "parse": lambda data: _parse_igdown(data)
    },
    {
        "name": "insta-saver",
        "url": "https://api.insta-saver.com/download",
        "method": "POST",
        "params": lambda url: None,
        "data": lambda url: {"url": url},
        "parse": lambda data: _parse_instasaver(data)
    }
]


def _parse_nyanpasu(data: dict) -> dict | None:
    if data.get("success") and data.get("media"):
        media = data["media"][0] if isinstance(data["media"], list) else data["media"]
        return {
            "media_url": media.get("url"),
            "type": media.get("type", "video"),
        }
    return None


def _parse_igdown(data: dict) -> dict | None:
    if data.get("status") == "success" and data.get("media"):
        media = data["media"]
        if isinstance(media, list):
            media = media[0]
        return {
            "media_url": media.get("download_url") or media.get("url"),
            "type": "video" if media.get("type") == "video" else "photo",
        }
    return None


def _parse_instasaver(data: dict) -> dict | None:
    if data.get("status") == 200 and data.get("data"):
        media_data = data["data"]
        return {
            "media_url": media_data.get("url") or media_data.get("video_url") or media_data.get("photo_url"),
            "type": "video" if media_data.get("video_url") else "photo",
        }
    return None


def extract_links(text: str) -> list:
    """Извлекает все ссылки на Instagram из текста"""
    pattern = r"https?://(?:www\.)?instagram\.com/(?:p|reel|stories|tv)/[a-zA-Z0-9_/?=&.-]+"
    matches = re.findall(pattern, text, re.IGNORECASE)
    links = []
    seen = set()
    for link in matches:
        link = re.sub(r"[.,!?;:)\s]+$", "", link)
        if link not in seen:
            seen.add(link)
            links.append(link)
    return links


def get_video_info(instagram_url: str) -> tuple[dict | None, str]:
    """Пробует сначала story-save.com, затем остальные API"""
    
    # 1. story-save.com
    logger.info(f"Пробую story-save.com для {instagram_url}")
    result = get_video_storysave(instagram_url)
    if result and result.get("media_url"):
        logger.info(f"✅ Успешно через story-save.com")
        return result, "story-save.com"
    
    # 2. Запасные API
    for api in API_LIST:
        try:
            logger.info(f"Пробую API: {api['name']} для {instagram_url}")
            
            headers = api.get("headers", {"User-Agent": USER_AGENT})
            
            if api["method"] == "GET":
                response = requests.get(
                    api["url"],
                    params=api["params"](instagram_url),
                    headers=headers,
                    timeout=15
                )
            else:
                response = requests.post(
                    api["url"],
                    data=api["data"](instagram_url),
                    headers=headers,
                    timeout=15
                )
            
            if response.status_code != 200:
                logger.warning(f"API {api['name']} вернул {response.status_code}")
                continue
            
            if api["name"] == "snapinsta":
                result = api["parse"](response.text)
            else:
                result = api["parse"](response.json())
            
            if result and result.get("media_url"):
                logger.info(f"✅ Успешно через {api['name']}")
                return result, api["name"]
                
        except Exception as e:
            logger.warning(f"Ошибка API {api['name']}: {e}")
            continue
    
    logger.error(f"❌ Все API не сработали для {instagram_url}")
    return None, ""


def format_caption(username: str, requester_name: str = "", likes: str = None, comments: str = None) -> str:
    """Форматирует подпись с хештегами и статистикой"""
    caption = f"#Instagram #{username}"
    if requester_name:
        caption += f" #{requester_name}"
    
    # Добавляем статистику если есть
    if likes or comments:
        caption += "\n\n"
        if likes:
            caption += f"❤️ {likes}"
        if likes and comments:
            caption += "  •  "
        if comments:
            caption += f"💬 {comments}"
    
    return caption


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений с ссылками на Instagram"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    chat_id = update.effective_chat.id
    
    if text.startswith('/'):
        return
    
    links = extract_links(text)
    
    if not links:
        return
    
    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.UPLOAD_VIDEO)
    
    # Имя того, кто запросил видео
    requester = update.effective_user.username or update.effective_user.first_name or ""
    if requester:
        requester = requester.replace(" ", "_")
    
    for link in links[:5]:
        try:
            video_info, api_name = get_video_info(link)
            
            if not video_info or not video_info.get("media_url"):
                await update.message.reply_text(
                    f"❌ Не удалось скачать видео\n\n{link}",
                    disable_web_page_preview=True
                )
                continue
            
            media_url = video_info["media_url"]
            media_type = video_info.get("type", "video")
            
            # Берём username из ответа API, если нет — извлекаем из ссылки
            username = video_info.get("username")
            if not username:
                username = "instagram_user"
            
            likes = video_info.get("likes")
            comments = video_info.get("comments")
            
            caption = format_caption(username, requester, likes, comments)
            
            # Кнопки
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Скачать", url=media_url)],
                [InlineKeyboardButton(f"🔍 @{username}", url=f"https://instagram.com/{username}")]
            ])
            
            # Пробуем отправить видео
            try:
                if media_type == "video":
                    await context.bot.send_video(
                        chat_id=chat_id,
                        video=media_url,
                        caption=caption,
                        supports_streaming=True,
                        reply_markup=keyboard,
                        reply_to_message_id=update.message.message_id
                    )
                else:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=media_url,
                        caption=caption,
                        reply_markup=keyboard,
                        reply_to_message_id=update.message.message_id
                    )
                
                logger.info(f"✅ Отправлено через {api_name}: @{username}")
                
            except Exception as e:
                # Если не удалось отправить медиа — только текст с кнопкой
                logger.warning(f"Не удалось отправить медиа: {e}")
                
                await update.message.reply_text(
                    f"📹 *Видео готово!*\n\n{caption}",
                    parse_mode=constants.ParseMode.MARKDOWN,
                    reply_markup=keyboard,
                    reply_to_message_id=update.message.message_id
                )
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Ошибка обработки ссылки {link}: {e}")


async def shpite_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'шпите'"""
    if not update.message or not update.message.text:
        return
    
    if 'шпите' in update.message.text.lower():
        await update.message.reply_text("😴 Ну шпите, шпите...")
        logger.info(f"💤 Ответил 'Ну шпите, шпите...'")