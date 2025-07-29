import re
import fitz  # PyMuPDF
import argparse

def extract_with_pymupdf(pdf_path):
    text = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        page_text = page.get_text()
        if page_text:
            text.append(page_text)
        else:
            print(f"[!] Страница {i + 1} не содержит текста.")
    return "\n".join(text)


def fix_hyphenated_words(text):
     # Склеивает переносы вида "technol-\nogy" → "technology"
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Склеивает переносы с пробелом (иногда так бывает): "technol- \nogy"
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

    # Удаляет лишние \n внутри предложений
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    return text


def replace_ligatures(text):
    return text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")


def remove_references_section(lines):
    patterns = [r'^references\b', r'^bibliography\b', r'^literature\b', r'^cited works\b']
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        for pattern in patterns:
            if re.match(pattern, line_lower) and len(line.split()) < 5:
                return lines[:i]  # Обрезаем всё после "References"
    return lines


def is_junk_line(line):
    line = line.strip()
    if not line or len(line) < 5:
        return True

    # Очень высокая доля не-алфавитных символов
    ratio = sum(1 for c in line if not c.isalnum() and c not in ".:;,-=+*/()[]") / len(line)
    if ratio > 0.5:
        return True

    # Очень мало гласных — почти наверняка псевдокод/формула
    if sum(c in 'aeiouAEIOU' for c in line) < 2:
        return True

    # Подозрительные символы из PDF-искажений
    if re.search(r'[ð¼Þþ≠≈⁄∙⋅]', line):
        return True

    # Похоже на уравнение (много "d(...)/dt", скобки, Wmt, Cu, Fe и т.п.)
    if re.search(r'd[WQ][a-z]*\s*/\s*dt', line, re.IGNORECASE):
        return True
    if re.search(r'[[]?[A-Z][a-z]?[a-z]?[¼=]', line):
        return True

    return False

def filter_pymupdf_output(text):
    # Склеивание переносов слов
    text = fix_hyphenated_words(text)

    # Замена лигатур
    text = replace_ligatures(text)

    # Удаление "грязных" строк
    lines = text.splitlines()
    clean_lines = [line for line in lines if not is_junk_line(line)]

    clean_lines = remove_references_section(clean_lines)
    # return "\n".join(clean_lines)
    # Слияние перенесённых строк (если они заканчиваются без точки)
    merged_lines = []
    buffer = ""
    for line in clean_lines:
        if buffer and not buffer.endswith(('.', ':', ';', '?')):
            buffer += " " + line.strip()
        else:
            if buffer:
                merged_lines.append(buffer.strip())
            buffer = line.strip()
    if buffer:
        merged_lines.append(buffer.strip())

    return "\n".join(merged_lines)


# === CLI-интерфейс ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Извлечение очищенного текста из PDF")
    parser.add_argument("pdf_path", help="Путь к PDF-файлу")
    parser.add_argument("output_path", help="Путь к выходному .txt файлу")
    args = parser.parse_args()
    
    result = extract_with_pymupdf(args.pdf_path)
    filtered_result = filter_pymupdf_output(result)

    with open(args.output_path, "w", encoding="utf-8") as f:
        f.write(filtered_result)

    print(f"✅ Очищенный и объединённый текст сохранён в: {args.output_path}")