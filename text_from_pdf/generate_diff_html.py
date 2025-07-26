import difflib
import argparse

def generate_html_diff(file1_path, file2_path, output_html_path):
    with open(file1_path, 'r', encoding='utf-8') as f1:
        text1 = f1.readlines()

    with open(file2_path, 'r', encoding='utf-8') as f2:
        text2 = f2.readlines()

    # Генерация различий с подсветкой
    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=100)
    html_diff = differ.make_file(text1, text2, fromdesc='Raw Text', todesc='Cleaned Text')

    with open(output_html_path, 'w', encoding='utf-8') as output:
        output.write(html_diff)

    print(f"✅ Визуальное сравнение сохранено: {output_html_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сравнение двух текстов и генерация HTML-файла.")
    parser.add_argument("raw_text", help="Путь к исходному (сырым) тексту")
    parser.add_argument("cleaned_text", help="Путь к очищенному тексту")
    parser.add_argument("output_html", help="Путь для сохранения HTML-файла")

    args = parser.parse_args()

    generate_html_diff(args.raw_text, args.cleaned_text, args.output_html)