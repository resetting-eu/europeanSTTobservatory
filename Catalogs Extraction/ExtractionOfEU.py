import fitz
from pprint import pprint
import json
import re
from bs4 import BeautifulSoup
import sys
import base64

sys.path.insert(0, '../Scottish')
from CommonFunctions import get_corresponding_link, compare_patterns

soup = BeautifulSoup('<html></html>', 'html.parser')
# eu_catalog = "../../Catalogs/EU/2024-leading-practices-in-smart-tourism.pdf"
# eu_catalog = "../../Catalogs/EU/2023-leading-practices-in-smart-tourism.pdf"
eu_catalog = "../../Catalogs/EU/2022-leading-practices-in-smart-tourism.pdf"
# catalog = "EU 2024"
# catalog = "EU 2023"
catalog = "EU 2022"
eu_patterns = json.load(open(f"{catalog} Patterns.json", "r"))
# first_page, last_page = 7, 53  # EU 2024
# first_page, last_page = 7, 72  # EU 2023
first_page, last_page = 9, 88  # EU 2022


def add_to_subsubcategory():
    global stt_application, application_description
    p = soup.new_tag('p')
    p.string = application_description.strip()
    stt_application[0]['description'] = str(p)
    h2 = soup.new_tag('h2')
    h2.string = stt_application[1]
    subsubcategory[0][str(h2)] = stt_application[0]
    # print(f"Add do subsub: {subsubcategory[1]}")
    stt_application = {}, ""
    application_description = ""


def is_stt_application():
    global subsubcategory, stt_application, application_description, new_application_name
    # print(f"Adding STT Application: {subsubcategory[1]}")
    if application_description.endswith("<br>"):
        application_description = application_description[:-4]
    # print(f"STT Application {stt_application[1]}")
    if stt_application[1] != "":
        add_to_subsubcategory()

    # print(span['text'])
    if ";" in new_application_name[0]:
        stt_fields = new_application_name[0].split(";")
    elif new_application_name[0].count(":") > 1:
        stt_fields = new_application_name[0].split(":")
    else:
        stt_fields = new_application_name[0].split(",")
    # print(stt_fields)
    stt_name = stt_fields[0]
    stt_application = {
        'bbox': new_application_name[1],
        'page': [page_number]
    }, stt_name
    if len(stt_fields) > 1:
        stt_localization = stt_fields[1].replace(":", "").strip()
        stt_application[0]['localization'] = stt_localization
    # print(stt_application[1])
    application_description = ""
    new_application_name = "", (0, 0, 0, 0)


def add_to_subcategory():
    global subsubcategory
    if stt_application[1] != "":
        add_to_subsubcategory()
    subcategory[0][subsubcategory[1]] = subsubcategory[0]

    subsubcategory = {}, ""


def is_subsubcategory():
    global subcategory, subsubcategory, new_subsubcategory_name
    # print(f"Adding subsubcategory: {subsubcategory[1]}")
    if subsubcategory[1] != "":
        add_to_subcategory()
    # print("New subsub name: ", new_subsubcategory_name)
    if ":" in new_subsubcategory_name:
        match = re.search(r'\d+(\.\d+)*\.?\s(.+?):', new_subsubcategory_name)
    elif ";" in new_subsubcategory_name:
        match = re.search(r'\d+(\.\d+)*\.?\s(.+?);', new_subsubcategory_name)
    else:
        match = re.search(r'\d+(\.\d+)*\.?\s(.+?),', new_subsubcategory_name)

    if match:
        name = match.group(2)
    else:
        name = "No match found"
    subsubcategory = {}, name.strip()
    new_subsubcategory_name = ""


def add_to_category():
    global subcategory
    add_to_subcategory()
    category[0][subcategory[1]] = subcategory[0]

    subcategory = {}, ""


def is_subcategory():
    global category, subcategory
    # print(f"Adding subcategory: {subcategory[1]}")
    if subcategory[1] != "":
        add_to_category()

    match = re.search(r'\d+(\.\d+)*\s(.+)', span['text'])
    if match:
        name = match.group(2)
    else:
        name = "No match found"
    subcategory = {}, name.strip()


def subcategory_or_subsubcategory():
    global new_subsubcategory_name
    # The patterns are the same for both subcategory and subsubcategory,
    # so we need to check the length of the section
    section = span['text'].strip().split(" ")[0]
    section_length = section.count(".")

    if section_length == 2:
        is_subcategory()
    else:
        new_subsubcategory_name += span['text']


def subsubcategory_or_stt_application():
    global new_subsubcategory_name, new_subsubcategory_bbox, new_subsub_page
    section = span['text'].strip().split(" ")[0]
    section_length = section.count(".")
    # print(f"{span['bbox'][1] - new_subsubcategory_bbox[1]}\n{span['text']}")
    if (section_length > 1 or
            (page_number == new_subsub_page and new_subsubcategory_bbox != (0, 0, 0, 0)
             and span['bbox'][1] - new_subsubcategory_bbox[1] < 17)):
        # print(f"New subsub: {span['text']}")
        if stt_application[1] != "":
            add_to_subsubcategory()
        new_subsubcategory_name += span['text']
        new_subsubcategory_bbox = span['bbox']
        new_subsub_page = page_number
    else:
        analyze_stt_application()


def add_to_categories():
    global categories, category
    # print(f"Adding category: {category[1]}")
    add_to_category()
    categories[category[1]] = category[0]


def start_analysing_new_category():
    global category
    if category[1] != "":
        add_to_categories()

    category = {}, span['text'].split("BEST PRACTICES IN")[-1].strip()


def check_if_application_it_is_on_more_than_one_page():
    if 'page' in stt_application[0] and page_number not in stt_application[0]['page']:
        stt_application[0]['page'].append(page_number)


def add_or_append_image(application, rights):
    if 'image_subtitles' not in application:
        application['image_subtitles'] = [rights]
    else:
        application['image_subtitles'].append(rights)
    return application


def add_author_rights_to_image():
    global stt_application
    rights = {'bbox': span['bbox'], 'page': page_number, 'text': span['text']}
    # print("\n")
    # print(page_number > stt_application[0]['page'][-1])
    # print(f"Page Number:  {page_number}, Author: {span['text']}")
    # # print(stt_application[0]['page'][-1])
    # print(stt_application[1])
    if (page_number == stt_application[0]['page'][0] and stt_application[0]['bbox'][1] < span['bbox'][1]) \
            or (len(stt_application[0]['page']) > 1 and page_number > stt_application[0]['page'][0]):
        stt_application = add_or_append_image(stt_application[0], rights), stt_application[1]
    else:
        for key in reversed(list(subsubcategory[0].keys())):
            if (page_number == subsubcategory[0][key]['page'][0] and subsubcategory[0][key]['bbox'][1] < span['bbox'][
                1]) \
                    or (len(subsubcategory[0][key]['page']) > 1 and page_number in subsubcategory[0][key]['page'][1:]):
                # print(key)
                subsubcategory[0][key] = add_or_append_image(subsubcategory[0][key], rights)
                break


def analyze_application_description():
    global application_description
    if new_application_name[0] != "":
        # print(f"Adding new STT: {new_application_name[0]}")
        is_stt_application()

    if "©" in span['text']:
        add_author_rights_to_image()
    else:
        application_description += span['text'][2:] if span['text'].startswith(": ") else span['text']
    check_if_application_it_is_on_more_than_one_page()


def analyze_stt_application():
    global new_application_name
    # print(f"analyze_stt_application: {span['text']}")
    if new_subsubcategory_name != "":
        is_subsubcategory()
    if not span['text'].endswith(" "):
        span['text'] += " "
    new_application_name = new_application_name[0] + span['text'], span['bbox']
    # print(new_application_name)


def analyze_span():
    global category, subcategory, subsubcategory, stt_application, application_description, new_application_name, new_subsubcategory_name
    if compare_patterns(span, eu_patterns["Category"]) and span['text'] != " ":
        # print("Is Category")
        start_analysing_new_category()
    elif compare_patterns(span, eu_patterns["SubSubCategory"]) and span['text'] != " ":
        # In EU 2022 the SubSubCategory and STT Applications patterns are equal
        subsubcategory_or_stt_application()
    elif compare_patterns(span, eu_patterns["SubCategory"]) and span['text'] != " ":
        # print("Is SubCategory")
        # In EU 2024 the SubCategory and SubSubCategory patterns are equal
        subcategory_or_subsubcategory()
    elif compare_patterns(span, eu_patterns["STT_Application"]) and span['text'] != " " \
            and span['text'] != ", ":
        # in page 36 EU 2024 (starting from 0) there is a blod comma after "Innovative digital
        # municipal solutions; Tetovo"
        analyze_stt_application()
    elif compare_patterns(span, eu_patterns["Application_Description"]) and span['text'] != " ":
        # print("Is STT Description")
        analyze_application_description()
    elif compare_patterns(span, eu_patterns["Hyperlink"]):
        # print("Is Link")
        application_description += get_corresponding_link(span, doc, page_number)
        check_if_application_it_is_on_more_than_one_page()


def add_image(dictionary, image_block):
    image_data = base64.b64encode(image_block['image']).decode()
    if 'Images' in dictionary:
        dictionary['Images'].append(image_data)
    else:
        dictionary['Images'] = [image_data]
    return dictionary


def analyze_image():
    global stt_application
    for image_to_avoid in images_to_avoid:
        if (image_to_avoid[0] <= block['bbox'][0] <= image_to_avoid[2] and
                image_to_avoid[1] <= block['bbox'][1] <= image_to_avoid[3]):
            return

    image_data = base64.b64encode(block['image']).decode()
    image_dict = {"bbox": block['bbox'], "image": image_data}
    if page_number not in images:
        images[page_number] = [image_dict]
    else:
        images[page_number].append(image_dict)


categories = {}
images = {}
category = {}, ""
subcategory = {}, ""
subsubcategory = {}, ""
new_subsubcategory_name, new_subsubcategory_bbox, new_subsub_page = "", (0, 0, 0, 0), 0
stt_application = {}, ""
new_application_name = "", (0, 0, 0, 0)
application_description = ""
images_to_avoid = [(315.30010986328125, 24.149890899658203, 523.0451049804688, 67.94989013671875),
                   (294.30010986328125, 773.5, 522.9849243164062, 806.0499877929688)]

with fitz.open(eu_catalog) as doc:
    for page_number in range(first_page, last_page):
        page = doc[page_number]
        print("Page number: ", page_number)
        for index, block in enumerate(page.get_text('dict')['blocks']):
            if block['type'] == 0:
                # pprint(block)
                for line_index, line in enumerate(block['lines']):
                    for span_index, span in enumerate(line['spans']):
                        if span['text'] == " " and len(line['spans']) == 1 and application_description != "":
                            application_description += "<br>"
                        else:
                            analyze_span()
            elif block['type'] == 1:
                # print(f"Image: {block['bbox']}")
                analyze_image()
        if page_number == last_page - 1:
            add_to_categories()

# print(json.dumps(categories, indent=4))
with open(f"{catalog}.json", "w") as file:
    json.dump(categories, file, indent=4)

with open(f"{catalog} Images.json", "w") as file:
    json.dump(images, file, indent=4)
