from bs4 import BeautifulSoup
import os

# filename = "Marketing"
menu_filename = "menu.html"
folder = "STTs Classifications Pages with Menu"
info_folder = "Pages Information"


def aggregate_menu(cur_folder):
    for filename in os.listdir(cur_folder):
        if os.path.isdir(f"{cur_folder}/{filename}"):
            aggregate_menu(f"{cur_folder}/{filename}")
        else:
            save(f"{cur_folder}/{filename}")


def save(filename):
    filename = filename.replace(f"{info_folder}/", "")
    print("Saving: ", filename)

    filename_folder_path = f"{folder}/{os.path.dirname(filename)}"
    os.makedirs(filename_folder_path, exist_ok=True)

    with open(menu_filename, 'r', encoding='utf-8') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')

        for a_tag in soup.find_all('a'):
            if a_tag.string.strip() == filename:
                a_tag['style'] = ""

        root_table = soup.find('table')
        root_tr = root_table.find_all('tr')[0]

        td_information = root_tr.find_all('td')[0]

    with open(f"{info_folder}/{filename}", 'r', encoding='utf-8') as f:
        info = f.read()
        info_soup = BeautifulSoup(info, 'html.parser')
        td_information.append(info_soup)

    with open(f"{folder}/{filename}", "w") as file:
        file.write(soup.prettify())


aggregate_menu(info_folder)
