from PyPDF2 import PdfReader
import re


def add_osn_to_word(word):
    """
    Handle unexpected pattern violations caused by spaces and newlines

    - PyPDF2 may inject unexpected spaces when reading PDF
    """
    osn = r"[\s\n]?"  # optional space, newline

    return rf"{osn}" + rf"{osn}".join(rf"{letter}" for letter in word)


GMAIL_PATTERN = (
    rf"({add_osn_to_word('http')}s?"
    + r".*?"
    + rf"{add_osn_to_word('msg-f')}"
    + r".*?:\d+?"
    + r"\d+/\d+/\d+.*?\d+:\d+\s[A-Z]+\s*)?"  # datetime
    + rf"({add_osn_to_word('Gmail')}.*?{add_osn_to_word('receipt')})"
)


def get_full_txt_from_pdf(path):
    reader = PdfReader(path)
    full_txt = ""
    for page in reader.pages:
        full_txt += page.extract_text()
    return full_txt


def clean_full_txt(full_txt):
    """Remove all characters/ phrases that will interfere with parsing"""
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

    full_txt = re.sub(GMAIL_PATTERN, "", full_txt)
    return full_txt


def get_raw_items_from_pdf(path):
    # Load pdf to str

    matches = re.findall(
        rf"([\w\-_\s\']+\n)"  # name
        + rf"([\d\s]+\n?)"  # sku
        + rf"(\d+\s+x\s+\$\d+\.\d+)"  # unit at price
        + rf"({add_osn_to_word('Price:')}\s*\$\d+\.\d+/[^$\n]+\n?|\$\d+\.\d+\n?)?"  # price per unit
        + rf"(?:\$\d+\.\d+\s+\w+\n)?"  # price /w tax code may appear first
        + rf"({add_osn_to_word('Qty:')}\s*\d+\.?\d*?\w+)?",  # quantity of unit
        full_txt,
    )
    return matches
