import tkinter as tk
import copy
from bs4 import BeautifulSoup, Comment
import json

filename = "menu"


class Index:
    def __init__(self, title="", link="", parent=None):
        self.parent = parent
        self.title = title
        self.link = link
        self.subindexs = []

        if parent is not None:
            parent.add_subindex(self)

    def set_info(self, title, link):
        self.title = title
        self.link = link
        update_GUI(root_index)

    def add_subindex(self, index):
        self.subindexs.append(index)

    def remove_subindex(self, index):
        self.subindexs.remove(index)

    def get_depth(self):
        return self.parent.get_depth() + 1 if self.parent is not None else -1

    def __str__(self):
        text = f"Title: {self.title}, Link: {self.link}, Depth: {self.get_depth()}\n"
        for subindex in self.subindexs:
            text += subindex.__str__()
        return text


old_versions = []


def load_menu_from_json(parent, menu):
    for title, info in menu.items():
        index = Index(title, info["link"], parent)
        load_menu_from_json(index, info["subindexs"])


def check_if_there_is_menu_saved():
    try:
        with open(f"{filename}.json", "r") as file:
            menu = json.load(file)
            load_menu_from_json(root_index, menu)
    except FileNotFoundError:
        pass


def add_title_fields(frame, index, title="", link="", ):
    # print(f"Adding title fields, parent title {index.parent.title if index.parent is not None else 'None'}")
    title_label = tk.Label(frame, text="Title")
    title_label.pack(side=tk.LEFT)
    title_entry = tk.Entry(frame, width=50)
    title_entry.pack(side=tk.LEFT)
    title_entry.insert(0, title)

    link_label = tk.Label(frame, text="Link")
    link_label.pack(side=tk.LEFT)
    link_entry = tk.Entry(frame, width=50)
    link_entry.pack(side=tk.LEFT)
    link_entry.insert(0, link)

    if title == "":
        add_title_button = tk.Button(frame, text="Add Title",
                                     command=lambda: add_element(title_entry, link_entry, index))
        add_title_button.pack(side=tk.LEFT)
    else:
        update_button = tk.Button(frame, text="Update",
                                  command=lambda: update_element(index, title_entry, link_entry))
        update_button.pack(side=tk.LEFT)
        remove_title_button = tk.Button(frame, text="Remove Title",
                                        command=lambda: remove_element(index))
        remove_title_button.pack(side=tk.LEFT)


def update_GUI(index, frame=None):
    # print(f"Update GUI, Title is {index.title}")
    if index.parent is None:
        clean_root_frame()

    if frame is None:
        frame = tk.Frame(root)
        frame.pack(fill=tk.X, padx=0)

    total_subindexs = len(index.subindexs)

    for i, subindex in enumerate(index.subindexs):
        if i >= total_subindexs:
            break
        # print(f"Subindex, depth: {subindex.get_depth()}")
        sub_frame = tk.Frame(root)
        sub_frame.pack(fill=tk.X, padx=50 * subindex.get_depth())
        add_title_fields(frame=sub_frame, index=subindex, title=subindex.title, link=subindex.link)
        update_GUI(subindex, sub_frame)

    if index.parent is not None and index.title != "":
        if not index.subindexs:
            # print(f"Adding possible subtitle for parent {index.title}")
            sub_frame = tk.Frame(root)
            sub_frame.pack(fill=tk.X, padx=50 * (index.get_depth() + 1))
            add_title_fields(frame=sub_frame, index=Index(parent=index))

        if index.parent.subindexs[-1] == index:
            # print(f"Adding possible subtitle for parent {index.parent.title}")
            new_frame = tk.Frame(root)
            new_frame.pack(fill=tk.X, padx=50 * index.get_depth())
            add_title_fields(frame=new_frame, index=Index(parent=index.parent))

    elif total_subindexs == 0 and index.parent is None:
        new_frame = tk.Frame(root)
        new_frame.pack(fill=tk.X, padx=0)
        add_title_fields(frame=new_frame, index=Index(parent=index))

    # print(f"Ended Update GUI, Title is {index.title}")


def add_element(text_entry, link_entry, index):
    text = text_entry.get()
    link = link_entry.get()

    old_versions.append(copy.deepcopy(root_index))
    # print(f"Old_versions {old_versions[-1]}")
    # print(f"Adding element, text: {text}, link: {link}, Old_versions length: {len(old_versions)}")

    index.set_info(text, link)


def update_element(index, title_entry, link_entry):
    old_versions.append(copy.deepcopy(root_index))
    index.set_info(title_entry.get(), link_entry.get())


def remove_element(index):
    old_versions.append(copy.deepcopy(root_index))
    index.parent.remove_subindex(index)
    update_GUI(root_index)


def undo():
    # print(f"Undo, Old_versions length: {len(old_versions)}")
    global root_index
    if len(old_versions) > 0:
        root_index = old_versions[-1]
        print(old_versions[-1])
        old_versions.remove(root_index)
        # print(f"New root index, {root_index}")
        update_GUI(root_index)


def get_tree_depth(index):
    depth = 0
    while index.parent is not None:
        print(index.title)
        index = index.parent
        depth += 1
    return depth - 1


def create_html_menu(index, table):
    for subindex in index.subindexs:
        if subindex.title == "":
            break
        print(f"SubIndex: {subindex.title}")
        tr = soup.new_tag('tr')
        td_subindex = soup.new_tag('td')

        if index.parent is None:
            td_subindex['style'] = "border: 0;"
        else:
            depth = get_tree_depth(subindex)
            td_subindex['style'] = f"border: 0; padding-left: {depth * 20}px;"
        a_tag = soup.new_tag('a', href=subindex.link)
        a_tag.string = subindex.title
        a_tag['style'] = "text-decoration: none;"
        td_subindex.append(a_tag)
        tr.append(td_subindex)
        table.append(tr)

        if subindex.subindexs and len(subindex.subindexs) > 1:
            # table_subindex = soup.new_tag('table')
            # table_subindex['style'] = "border: 0;"
            # td_subindex.append(create_html_menu(subindex, table_subindex))
            create_html_menu(subindex, table)


def save_menu_in_json(index):
    menu = {}

    for subindex in index.subindexs:
        menu[subindex.title] = {
            "link": subindex.link,
            "subindexs": save_menu_in_json(subindex)
        }

    # It means that index is root and have iterated over all subindexs
    if index.parent is None:
        with open(f"{filename}.json", "w") as file:
            json.dump(menu, file, indent=4)

    return menu


def generate_html():
    global root_index, soup

    table_menu = soup.find_all('table')[1]
    create_html_menu(root_index, table_menu)

    save_menu_in_json(root_index)

    with open(f"{filename}.html", "w") as file:
        file.write(soup.prettify())


def clean_root_frame():
    global root
    for widget in root.winfo_children():
        widget.destroy()


def initialize_html_parser():
    soup_parse = BeautifulSoup("", "html.parser")

    table = soup_parse.new_tag("table")
    table['style'] = "width: 100%; border: 0;"

    tr = soup_parse.new_tag('tr')

    # Adding the left column for information to be displayed
    td_information = soup_parse.new_tag('td')
    td_information['style'] = "width: 75%; border: 0;"
    td_information.append(Comment("INFORMATION HERE"))
    tr.append(td_information)

    # Adding the right column for the menu
    td_menu = soup_parse.new_tag('td')
    td_menu['style'] = "width: 25%; border: 0; vertical-align: top;"
    td_menu.append(Comment("MENU FROM HERE"))
    table_menu = soup_parse.new_tag('table')
    table_menu['style'] = "border: 0;"
    td_menu.append(table_menu)
    tr.append(td_menu)

    table.append(tr)
    soup_parse.append(table)

    return soup_parse


# Creating the graphical interface
root_main = tk.Tk()
root_main.geometry("1200x700")

canvas = tk.Canvas(root_main)
scrollbar = tk.Scrollbar(root_main, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
root = tk.Frame(canvas)
canvas.create_window((0, 0), window=root, anchor='nw')

# Creating the hierarchical structure for the menu
root_index = Index(title="root")
# Checking if there is a menu saved
check_if_there_is_menu_saved()
# Initialize the html parser
soup = initialize_html_parser()
# Adding to the graphical interface the current hierarchical structure, which for now is empty
update_GUI(root_index)

generate_html_button = tk.Button(root_main, text="Generate HTML", command=generate_html)
generate_html_button.pack(side=tk.BOTTOM)
undo_button = tk.Button(root_main, text="Undo", command=undo)
undo_button.pack(side=tk.LEFT, anchor='sw')

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
root_main.update()
canvas.config(scrollregion=canvas.bbox("all"))
# To keep the graphical interface open
root.mainloop()
