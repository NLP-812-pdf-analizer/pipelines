import fitz  # PyMuPDF
import argparse
import re

# === Удаление "мусорных" блоков ===

def is_noise_block(text, bbox, page_height):
    text = text.strip()
    _, y0, _, y1 = bbox

    # ВЕРХ страницы или НИЗ страницы
    if y1 < 100 or y0 > page_height - 100:
        return True

    # Очень короткий текст (менее 30 символов)
    if len(text) < 30:
        return True

    # Весь текст в верхнем регистре и не содержит точек (подписи, заголовки, номера рисунков)
    if text.isupper() and '.' not in text and len(text.split()) < 6:
        return True

    # Мало букв, много символов или цифр (например: "© 2023, v1.2", или DOI)
    if re.match(r'^[\W\d\s]+$', text):
        return True

    return False

def is_table_block(text):
    lines = text.strip().split('\n')
    digit_lines = sum(1 for line in lines if re.search(r'\d{2,}', line))
    return len(lines) >= 3 and digit_lines / len(lines) > 0.5

def is_equation_like(text):
    return bool(re.search(r'[=><\^×\*\[\]]', text)) or re.search(r'\bK\d+\b', text)

def is_caption_line(text):
    text = text.strip()
    # Оставляем Figure 6 shows ...
    if re.match(r'^\s*(Fig(\.|ure)?|Figure)\s*\d+\s+(shows|illustrates|demonstrates)', text, re.IGNORECASE):
        return False
    # Удаляем: Fig. 2., Table I:, Eq. [3]
    if re.match(r'^\s*(Fig(\.|ure)?|Figure|Table|Eq(uation)?)(\s+\w+)?\s*(\.|:)?\s*$', text, re.IGNORECASE):
        return True
    return False


def remove_references(lines):
    digit_refs = []  # для 1. 2. 3.
    bracket_refs = []  # для [1] [2] [3]

    for i in range(len(lines)):
        line = lines[i].strip()
        if re.match(r'^\d+\.\s*$', line):  # 1.
            digit_refs.append(i)
        elif re.match(r'^\[\d+\]', line):  # [1]
            bracket_refs.append(i)

    # Удалить с первой ссылки, если найдено 3 или более подряд ссылок
    if len(digit_refs) >= 3:
        return lines[:digit_refs[0]]
    if len(bracket_refs) >= 3:
        return lines[:bracket_refs[0]]

    return lines

# === Объединение разорванных строк ===


def merge_broken_lines(lines):
    merged = []
    current = ""

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Проверка переноса слова через дефис
        if line.endswith('-') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # Склеиваем без дефиса
            line = line[:-1] + next_line
            i += 1  # пропустить следующую строку

        # Проверка завершения предложения
        if re.search(r'[.!?…]["”\']?$|[:;]$|^\s*[-–•]', line):
            if current:
                merged.append(current + " " + line if current else line)
                current = ""
            else:
                merged.append(line)
        else:
            current = current + " " + line if current else line

        i += 1

    if current:
        merged.append(current)

    return [re.sub(r'\s+', ' ', m.strip()) for m in merged]

# === Основная функция ===

def extract_lapdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    all_lines = []

    for page in doc:
        page_height = page.rect.height
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (round(b[1], 1), b[0]))

        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if is_noise_block(text, (x0, y0, x1, y1), page_height):
                continue
            if is_table_block(text):
                continue
            # if is_equation_like(text):
            #     continue
            # if is_caption_line(text):
            #     continue

            # Расщепляем по \n внутри блока
            lines = text.strip().split('\n')
            all_lines.extend(lines)

    # Объединение строк в предложения
    clean_lines = merge_broken_lines(all_lines)
    
    # Удаление списка литературы
    clean_lines = remove_references(clean_lines)

    return '\n'.join(clean_lines)

# === CLI-интерфейс ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Извлечение очищенного текста из PDF")
    parser.add_argument("pdf_path", help="Путь к PDF-файлу")
    parser.add_argument("output_path", help="Путь к выходному .txt файлу")
    args = parser.parse_args()
    
    result = extract_lapdf_text(args.pdf_path)
    with open(args.output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"✅ Очищенный и объединённый текст сохранён в: {args.output_path}")