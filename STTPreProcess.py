import os
import pyautogui
from hugchat import hugchat
from hugchat.login import Login
from PyPDF2 import PdfReader

from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

COOKIE_PATH_DIR = "./cookies_snapshot"
STT_PROMPT_DIR = "Prompts/STT_Prompt.txt"
STT_SPAIN_PROMPT_DIR = "Prompts/STT_Prompt_Spain.txt"


def create_hugchat_chatbot(email):
    if not os.path.exists(COOKIE_PATH_DIR):
        os.mkdir(COOKIE_PATH_DIR)

    files = os.listdir(COOKIE_PATH_DIR)

    if email + ".json" in files:
        # The user has already logged in before
        sign = Login(email, None)
        cookies = sign.loadCookiesFromDir(COOKIE_PATH_DIR)
    else:
        # The user has not logged in before. pwinput is to hide the password input
        # password = input("Password: ")
        password = pyautogui.password(text="", title="Password", mask="*")
        sign = Login(email, password)
        cookies = sign.login()
        sign.saveCookiesToDir(COOKIE_PATH_DIR)

    return hugchat.ChatBot(cookies=cookies.get_dict())


def extract_text_from_pdf(pdf_path):
    pdf = PdfReader(open(pdf_path, 'rb'))
    pdf_text = ""

    for page in pdf.pages:
        pdf_text += page.extract_text()

    return pdf_text


def extract_text_from_pdf_from_spanish_catalogue(pdf_path):
    fp = open('RandomisedSample/128_APP&TOWN COMPAGNON.pdf', 'rb')
    resource_manager = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(resource_manager, laparams=laparams)
    interpreter = PDFPageInterpreter(resource_manager, device)
    pages = PDFPage.get_pages(fp)

    stt_pdf_text = ""
    parties_pdf_text = ""
    for page in pages:
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
                if x > 350:  # Only get the text on the right side of the page
                    stt_pdf_text += "\n" + text
                elif y > 50:
                    parties_pdf_text += "\n" + text

    return stt_pdf_text, parties_pdf_text


def load_prompt_from_txt_file(prompt_dir):
    with open(prompt_dir, 'r', encoding='utf-8') as f:
        return f.read()


class STTPreProcess:

    def __init__(self, email):
        self.chatbot = create_hugchat_chatbot(email)

    def run(self, pdf_path, spain_catalogue):
        if spain_catalogue:
            pdf_text, parties_pdf_text = extract_text_from_pdf_from_spanish_catalogue(pdf_path)
            stt_prompt = load_prompt_from_txt_file(STT_SPAIN_PROMPT_DIR)
            prompt = f"""{stt_prompt} ```{pdf_text}```. ```{parties_pdf_text}```"""

            # Falta alterar a prompt para fazer referência aos dois textos delimitados por ```.
        else:
            pdf_text = extract_text_from_pdf(pdf_path)
            stt_prompt = load_prompt_from_txt_file(STT_PROMPT_DIR)
            prompt = f"""{stt_prompt} ```{pdf_text}```"""

        response = self.chatbot.chat(prompt, 0.1)

        json_list_final = response.rfind('\n]')
        json_list_start = response.find('[\n')
        indices = [0, json_list_start, json_list_final + 2]  # +1 -> \n; +2 -> \n]
        parts = [response[i:j] for i, j in zip(indices, indices[1:] + [None])]
        return parts[1]
