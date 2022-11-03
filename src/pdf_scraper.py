from PyPDF2 import PdfReader
import re


def add_osn_to_word(word):
    """
    Handle unexpected pattern violations caused by spaces and newlines

    - PyPDF2 may inject unexpected spaces when reading PDF
    """
    osn = r"[\s\n]?"  # optional space, newline

    return rf"{osn}" + rf"{osn}".join(rf"{letter}" for letter in word)


def get_raw_items_from_pdf(path):
    import os

    print(os.getcwd())
    # Load pdf to str
    reader = PdfReader(path)
    full_txt = ""
    for page in reader.pages:
        full_txt += page.extract_text()

    # Remove/Replace unnecessary chars
    full_txt = full_txt.replace("\xa0", "")
    full_txt = full_txt.replace("×", "x")

    # Remove prefix text
    full_txt = full_txt[
        re.search(rf"{add_osn_to_word('Groceries')}:", full_txt).end() :
    ]

    # Remove suffix text
    full_txt = full_txt[
        : re.search(add_osn_to_word("Payment Information"), full_txt).start()
    ]

    matches = re.findall(
        rf"([\w\-_\s\d\']+\n)"  # name
        + rf"([\d\s]+\n?)"  # sku
        + rf"(\d+\s+x\s+\$\d+\.\d+)"  # unit at price
        + rf"({add_osn_to_word('Price:')}\s*?\$\d+\.\d+/\w+\n?|\$\d+\.\d+\n)?"  # price per unit
        + rf".*?"
        + rf"({add_osn_to_word('Qty:')}\s*\d+\.?\d*?\w+)?",  # quantity of unit
        full_txt,
    )
    print([full_txt])
    return matches
