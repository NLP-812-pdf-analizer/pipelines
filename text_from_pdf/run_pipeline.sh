#!/bin/bash

# Проверка аргументов
if [ $# -lt 1 ]; then
    echo "❗ Укажите путь к PDF-файлу:"
    echo "Пример: ./run_pipeline.sh ./input/article.pdf"
    exit 1
fi

PDF_PATH="$1"
RAW_TXT="test/raw.txt"
CLEANED_TXT="test/cleaned.txt"
DIFF_HTML="test/diff_report.html"

echo "📄 PDF-файл: $PDF_PATH"
echo "🔄 Извлечение полного текста..."

# 1. Извлечь сырой текст
python extract_raw_text.py "$PDF_PATH" "$RAW_TXT" || { echo "❌ Ошибка извлечения raw текста"; exit 1; }

# 2. Извлечь очищенный текст
python extract_clean_text.py "$PDF_PATH" "$CLEANED_TXT" || { echo "❌ Ошибка извлечения clean текста"; exit 1; }

# 3. Сравнение diff в HTML
python generate_diff_html.py "$RAW_TXT" "$CLEANED_TXT" "$DIFF_HTML" || { echo "❌ Ошибка генерации HTML сравнения"; exit 1; }

# # 4. Запуск автотестов
# echo "🧪 Запуск тестов..."
# python test_text_extraction.py || { echo "❌ Ошибка тестов"; exit 1; }

echo ""
echo "✅ Все этапы выполнены успешно."
echo "📂 Файлы:"
echo " - Полный текст:      $RAW_TXT"
echo " - Очищенный текст:   $CLEANED_TXT"
echo " - HTML сравнение:    $DIFF_HTML"
echo ""
echo "🌐 Открой diff_report.html в браузере для визуального сравнения."