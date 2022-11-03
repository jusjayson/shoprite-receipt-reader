from PyPDF2 import PdfReader
import re


def add_osn_to_word(word):
    """
    Handle unexpected pattern violations caused by spaces and newlines

    - PyPDF2 may inject unexpected spaces when reading PDF
    """
    osn = r"(\s\n)?"  # optional space, newline

    return rf"{osn}" + rf"{osn}".join(rf"{letter}" for letter in word)


def get_raw_items_from_pdf(path):
    import os

    print(os.getcwd())
    # Load pdf to str
    reader = PdfReader(path)
    full_txt = ""
    for page in reader.pages:
        full_txt += page.extract_text()

    # Remove unnecessary chars
    full_txt = full_txt.replace("\xa0", "")

    # Remove prefix text
    full_txt = full_txt[
        re.search(rf"{add_osn_to_word('Groceries')}:", full_txt).end() :
    ]

    # Remove suffix text
    full_txt = full_txt[
        : re.search(add_osn_to_word("Payment Information"), full_txt).start()
    ]

    print([full_txt])
    return []
