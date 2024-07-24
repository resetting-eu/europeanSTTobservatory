import fitz
from pprint import pprint
import json

segitur_2023 = "../Catalogs/Segittur/Catalogue_Spanish_2023.pdf"
segitur_2022 = "../Catalogs/Segittur/Catalogue Spanish_2022.pdf"

pdf = fitz.open(segitur_2023)
# pdf = fitz.open(segitur_2022)
filename = "Titles_2023.json"
# filename = "Titles_2022.json"
first_page, last_page = 9, 363
# first_page, last_page = 11, 263
# first_page, last_page = 36, 37

"""
(0,0) is the top-left corner of the page
bbox = (x1,y1,x2,y2)
(x1,y1) = top-left corner
(x2,y2) = bottom-right corner
"""


def check_bbox(bbox):
    if "2023" in filename:
        if (387 < bbox[0] < 390 and bbox[1] > 104 and
                bbox[2] < 1200 and bbox[3] < 500):
            return True
        return False
    elif "2022" in filename:
        if (391 < bbox[0] < 395 and 97 < bbox[1] < 105 and
                bbox[2] < 1200 and bbox[3] < 500):
            return True
        return False


def remove_mixed_case_words(s):
    words = s.split()
    new_words = []

    for word in words:
        if word.isupper() or word.islower():
            new_words.append(word)

    return ' '.join(new_words)


def get_titles(pdf, page_start, page_end):
    titles = []
    for page_number in range(page_start, page_end):
        page = pdf[page_number]
        title = ""
        for block in page.get_text('dict')['blocks']:
            # if page_number == 114:
            # pprint(block)  # Use pprint instead of print
            if check_bbox(block['bbox']):
                if "lines" in block.keys():
                    for line in block['lines']:
                        for span in line['spans']:
                            text = remove_mixed_case_words(span['text'])
                            if text.isupper():
                                title += span['text']
        # print(f"Page: {page_number}, {title}")
        titles.append((page_number, title))

    return titles


# Comparing Titles_2023.json and Titles_2022.json
with open("Titles_2023.json", "r", encoding='utf-8') as file:
    titles_2023 = json.load(file)
with open("Titles_2022.json", "r", encoding='utf-8') as file:
    titles_2022 = json.load(file)

total = 0
repetitions = {}

for title in titles_2023.keys():
    if title in titles_2022.keys():
        repetitions[title] = {
            "2023": titles_2023[title],
            "2022": titles_2022[title]
        }
        # print(f"Title: {title}, Page 2023: {titles_2023[title]}, Page 2022: {titles_2022[title]}")
        total += 1

with open("Repetitions.json", "w", encoding='utf-8') as file:
    file.write(json.dumps(repetitions, indent=4))

print(f"Total Titles in both Catalogs: {total}\nTotal Titles in 2022: {len(titles_2022)}\nTotal Titles in 2023: {len(titles_2023)}")


"""
Total Titles in both Catalogs: 168
Total Titles in 2022: 247
Total Titles in 2023: 349
"""