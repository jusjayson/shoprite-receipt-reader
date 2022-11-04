from PyPDF2 import PdfReader
import re


def add_osn_to_word(word):
    """
    Handle unexpected pattern violations caused by spaces and newlines

    - PyPDF2 may inject unexpected spaces when reading PDF
    """
    osn = r"(?:[\s\n]?)"  # optional space, newline

    return rf"{osn}" + rf"{osn}".join(rf"{letter}" for letter in word)


def strip_new_lines(pattern):
    return rf"(?:\n*){pattern}(?:\n*)"


GMAIL_URL_PATTERN = (
    rf"{add_osn_to_word('http')}s?"
    + r".*?"
    + rf"{add_osn_to_word('msg-f')}"
    + r".*?:\d+"
)
GMAIL_DT_PATTERN = r"\d+/\d+/\d+.*?\d+:\d+\s[A-Z]+\s*"
GMAIL_NAME_PATTERN = rf"{add_osn_to_word('Gmail')}.*?{add_osn_to_word('receipt')}"
GMAIL_PATTERN = rf"{GMAIL_URL_PATTERN}{GMAIL_DT_PATTERN}{GMAIL_NAME_PATTERN}|{GMAIL_DT_PATTERN}{GMAIL_NAME_PATTERN}{GMAIL_URL_PATTERN}|{GMAIL_NAME_PATTERN}"
PRICE_W_TAX_CODE_PATTERN = r"\$\d+\.\d+\s*[A-Z]+[\n\s]*"


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


snl = r"(?:[\s\n]*)"


ITEM_NAME_PATTERN = rf"[\w\-_ \t\']+"


def get_raw_items_from_pdf(path):
    # Load pdf to str

    full_txt = get_full_txt_from_pdf(path)
    full_txt = clean_full_txt(full_txt)
    print([full_txt])
    matches = re.findall(
        rf"({ITEM_NAME_PATTERN}){snl}"  # name
        + rf"([0-9 \t]+){snl}"  # sku
        + rf"([0-9]+[ \t]+x[ \t]+\$[0-9]+\.[0-9]+){snl}"
        # unit at price
        + rf"(\*+[A-Z]+\*+{ITEM_NAME_PATTERN}[ \t]*:[ \t]*\$[0-9]+\.[0-9]+)?{snl}"  # coupon codes
        + rf"({add_osn_to_word('Price:')}\s*\$[0-9]+\.[0-9]+/[^$\n]+\n?|\$[0-9]+\.[0-9]+\n?)?{snl}"  # price per unit
        + rf"(?:{PRICE_W_TAX_CODE_PATTERN})?"  # price /w tax code may appear first
        + r"(?:\d+/\d+\n?)?"  # page num may appear first
        + rf"({add_osn_to_word('Qty')}:\s*[0-9]+\.[0-9]+[^$\n0-0]+)?"  # quantity of unit
        + rf"(?:{PRICE_W_TAX_CODE_PATTERN})?",  # price /w tax code may appear afterwards
        full_txt,
    )

    return matches
