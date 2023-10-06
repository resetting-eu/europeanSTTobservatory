from PyPDF2 import PdfReader

european_dir = "Catalogues/Catalogue European.pdf"

pdf = PdfReader(open(european_dir, 'rb'))

total_possible_stts = 0

for page_number in range(2, 6):
    page = pdf.pages[page_number]

    lines = page.extract_text().split("\n")
    for line_number in range(0, len(lines)):
        line = lines[line_number]

        # Check if the title is split into two lines
        if line_number + 1 < len(lines):
            next_line = lines[line_number + 1]
            if not next_line[0].isdigit():
                line += next_line

        total_possible_stts += line.count(";")

print("Total possible STTs: ", total_possible_stts)
