import tkinter as tk
from bs4 import BeautifulSoup
import os

filename = "Marketing"
menu_filename = "menu.html"
folder = "STTs Classification"

os.makedirs(folder, exist_ok=True)


def save():
    global filename
    with open(menu_filename, 'r') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')

        for a_tag in soup.find_all('a'):
            if a_tag.string.strip() == filename:
                a_tag['style'] = ""

        root_table = soup.find('table')
        root_tr = root_table.find_all('tr')[0]

        td_information = root_tr.find_all('td')[0]
        information = text_entry.get("1.0", tk.END)
        soup_information = BeautifulSoup(information, "html.parser")
        td_information.append(soup_information)

    if filename == "":
        filename = "Test"

    with open(f"{folder}/{filename}.html", "w") as file:
        file.write(soup.prettify())


root_main = tk.Tk()
root_main.geometry("1000x700")

text_entry = tk.Text(root_main)
text_entry.pack()
text_entry.place(width=1000, height=600)

save_button = tk.Button(root_main, text="Save", command=save)
save_button.pack(side=tk.BOTTOM)

root_main.mainloop()
