from pdf_scraper import get_parsed_items_from_pdf, import_master_info_from_csv

PDF_DIR = "./tests/test_data"


def test_import_master_info():
    master_info = import_master_info_from_csv(f"{PDF_DIR}/master.csv")
    assert master_info["1"]["Name"] == "Patayters"
    assert master_info["1"]["Cat"] == "Food"
    assert master_info["3"]["Name"] == "Iron"


def test_master_replaces_name_and_cat():
    parsed_item = get_parsed_items_from_pdf(
        f"{PDF_DIR}/shoprite_edited.pdf", f"{PDF_DIR}/master.csv"
    )[0]
    assert parsed_item["Name"] == "Fresh Brocolli"
    assert parsed_item["Cat"] == "Food"
