from PyPDF2 import PdfReader


def get_raw_items_from_pdf(path):
    import os

    print(os.getcwd())
    # Load pdf to str
    reader = PdfReader(path)
    full_txt = ""
    for page in reader.pages:
        full_txt += page.extract_text()

    full_txt = full_txt.replace("\xa0", "")

    print(full_txt)
    return []
