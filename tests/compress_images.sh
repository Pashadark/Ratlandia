#!/bin/bash
# СКРИПТ СЖАТИЯ ВСЕХ ФОТО С БЕКАПОМ
# Автор: Pashadark

echo "========================================"
echo "🖼️ СЖАТИЕ ВСЕХ ФОТО С БЕКАПОМ"
echo "========================================"

cd /root/bot || exit

# 1. Установить ImageMagick если нет
if ! command -v convert &> /dev/null; then
    echo "📦 Устанавливаю ImageMagick..."
    apt-get update
    apt-get install imagemagick -y
fi

# 2. Создать папку с бекапом
BACKUP_DIR="/root/bot/images_old_$(date +%Y%m%d_%H%M%S)"
echo "💾 Создаю бекап: $BACKUP_DIR"
cp -r /root/bot/images "$BACKUP_DIR"
echo "✅ Бекап создан!"

# 3. Сжать все фото
echo ""
echo "🖼️ Начинаю сжатие..."
TOTAL_BEFORE=0
TOTAL_AFTER=0
COUNT=0

# Пройти по всем jpg/png в папке images и подпапках
find /root/bot/images -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | while read file; do
    SIZE_BEFORE=$(stat -c%s "$file")
    TOTAL_BEFORE=$((TOTAL_BEFORE + SIZE_BEFORE))
    
    # Сжать
    convert "$file" -resize 800x800\> -quality 85 -strip "$file"
    
    SIZE_AFTER=$(stat -c%s "$file")
    TOTAL_AFTER=$((TOTAL_AFTER + SIZE_AFTER))
    COUNT=$((COUNT + 1))
    
    BEFORE_KB=$((SIZE_BEFORE / 1024))
    AFTER_KB=$((SIZE_AFTER / 1024))
    SAVED=$((BEFORE_KB - AFTER_KB))
    
    echo "  ✅ $(basename "$file"): ${BEFORE_KB}KB → ${AFTER_KB}KB (экономия ${SAVED}KB)"
done

# 4. Итоги
echo ""
echo "========================================"
echo "✅ СЖАТИЕ ЗАВЕРШЕНО!"
echo "📁 Обработано файлов: $COUNT"
echo "💾 Бекап: $BACKUP_DIR"
echo ""
echo "🔙 Для отката:"
echo "   rm -rf /root/bot/images"
echo "   cp -r $BACKUP_DIR /root/bot/images"
echo "========================================"