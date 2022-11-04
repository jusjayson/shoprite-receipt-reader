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
    r"(\d+/\d+/\d+.*?\d+:\d+\s[A-Z]{2})?"  # datetime
    + add_osn_to_word("Gmail")
    + r".*?"
    + add_osn_to_word("receipt")
    + r".*?"
    + rf"({add_osn_to_word('http')}s?"
    + r".*?"
    + rf"{add_osn_to_word('msg-f')}"  # message id
    + rf".*?:\d+?"
    + rf".*?\d+[\s\n]?/\d+)?"
)


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
    full_txt = re.sub(GMAIL_PATTERN, "", full_txt)

    # Remove prefix text
    full_txt = full_txt[
        re.search(rf"{add_osn_to_word('Groceries')}:", full_txt).end() :
    ]

    # Remove suffix text
    full_txt = full_txt[
        : re.search(add_osn_to_word("Payment Information"), full_txt).start()
    ]

    matches = re.findall(
        rf"([\w\-_\s\']+\n)"  # name
        + rf"([\d\s]+\n?)"  # sku
        + rf"(\d+\s+x\s+\$\d+\.\d+)"  # unit at price
        + rf"({add_osn_to_word('Price:')}\s*\$\d+\.\d+/[lb]*)+"  # price per unit
        # + rf"({add_osn_to_word('Price:')}\s*?\$\d+\.\d+/[lb]{2}\n?)?",  # price per unit
        # + rf".*?"
        + rf"({add_osn_to_word('Qty:')}\s*\d+\.?\d*?\w+)?",  # quantity of unit
        full_txt,
    )
    print([full_txt])
    return matches
    # + rf"({add_osn_to_word('Price:')}\s*?\$\d+\.\d+/\w{3,20}?\n?|\$\d+\.\d+\n?)?"  # price per unit


"\n BROC CRWNS RPC\n3082\n1 x $6.41\nPrice: $1.99/lb\nQty: 3.22lb\n 11/2/22, 5:19 PM"
"\n \n PEPPER HABANERO 10\n3125\n1 x $0.30\nPrice: $6.00/lb$0.30 FWT\nQty: 0.05lb\n"
r"Price:\s*\$\d+\.\d+/[lb]{2}\n?"
