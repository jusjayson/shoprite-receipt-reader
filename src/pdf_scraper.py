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
PRICE_W_TAX_CODE_PATTERN = r"\$\d+\.\d+\s*[A-Z]+"


def get_raw_items_from_pdf(path):
    # Load pdf to str

    full_txt = get_full_txt_from_pdf(path)
    full_txt = clean_full_txt(full_txt)
    matches = re.findall(
        rf"({ITEM_NAME_PATTERN}){snl}"  # name
        + rf"([0-9 \t]+){snl}"  # sku
        + rf"([0-9]+[ \t]+x[ \t]+\$[0-9]+\.[0-9]+){snl}"
        + rf"(\*+[A-Z]+\*+{ITEM_NAME_PATTERN}[ \t]*:[ \t]*\$[0-9]+\.[0-9]+)?{snl}"  # coupon codes
        + rf"({add_osn_to_word('Price:')}\s*\$[0-9]+\.[0-9]+/[^$\n]+|\$[0-9]+\.[0-9]+)?{snl}"  # price per unit
        + rf"(?:{PRICE_W_TAX_CODE_PATTERN})?{snl}"  # price /w tax code may appear first
        + r"(?:\d+/\d+\n?)?"  # page num may appear first
        + rf"({add_osn_to_word('Qty')}:\s*[0-9]+\.[0-9]+[^$\n0-0]+)?"  # quantity of unit
        + rf"(?:{PRICE_W_TAX_CODE_PATTERN})?{snl}",  # price /w tax code may appear afterwards
        full_txt,
    )

    return matches


def parse_raw_item(raw_item_and_iterable_and_master):
    raw_item, iterable, master_info = raw_item_and_iterable_and_master
    iterable.append(
        {
            "Name": master_info.get(raw_item[1], {}).get("Name")
            or raw_item[0].lstrip(),
            "SKU": raw_item[1],
            "Price per quantity": raw_item[2],
            "Price per unit": re.sub(r"Price:\s+", "", raw_item[4]) or None,
            "Quantity": re.sub(r"Qty:\s+", "", raw_item[5]) or None,
            "Cat": master_info.get(raw_item[1], {}).get("Cat"),
        }
    )


def import_master_info_from_csv(master_path):
    with open(master_path) as master_file:
        reader = csv.DictReader(master_file)
        return {row["SKU"]: {"Name": row["Name"], "Cat": row["Cat"]} for row in reader}


def get_parsed_items_from_pdf(import_path, master_path=None):

    master_info = import_master_info_from_csv(master_path) if master_path else {}
    parsed_items = Manager().list()
    raw_items = get_raw_items_from_pdf(import_path)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(
            parse_raw_item,
            [(raw_item, parsed_items, master_info) for raw_item in raw_items],
            timeout=60,
        )

    return parsed_items

