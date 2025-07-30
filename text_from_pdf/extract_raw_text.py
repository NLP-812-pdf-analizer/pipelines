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


# === CLI-интерфейс ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Извлечение текста из PDF без дальнейшей обрабоки")
    parser.add_argument("pdf_path", help="Путь к PDF-файлу")
    parser.add_argument("output_path", help="Путь к выходному .txt файлу")
    args = parser.parse_args()
    
    result = extract_with_pymupdf(args.pdf_path)

    with open(args.output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"✅ Очищенный и объединённый текст сохранён в: {args.output_path}")