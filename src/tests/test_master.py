import os
import pathlib
from pdf_scraper import (
    get_parsed_items_from_pdf,
    import_master_info_from_csv,
    update_master,
)

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
    assert parsed_item["Name"] == "Fresh Broccoli"
    assert parsed_item["Cat"] == "Food"


def test_update_master():
    new_master_path = f"{PDF_DIR}/new_master.csv"
    if os.path.isfile(new_master_path):
        os.remove(new_master_path)
    pathlib.Path(new_master_path).touch()
    master_info = import_master_info_from_csv(new_master_path)
    assert not master_info
    parsed_items = get_parsed_items_from_pdf(
        f"{PDF_DIR}/shoprite_edited.pdf", new_master_path
    )
    update_master(parsed_items, new_master_path)
    assert import_master_info_from_csv(new_master_path)


def test_update_master_with_preexisting_data():
    new_master_path = f"{PDF_DIR}/new_master.csv"
    if os.path.isfile(new_master_path):
        os.remove(new_master_path)
    update_master(
        [
            {
                "Name": "Fresh Broccoli",
                "SKU": "3082",
                "Price per quantity": "1 x $1.0",
                "Price per unit": "$1.49/lb",
                "Quantity": "1.0lb",
                "Cat": "Food",
            }
        ],
        new_master_path,
    )
    master_info = import_master_info_from_csv(new_master_path)
    assert len(master_info) == 1
    parsed_items = get_parsed_items_from_pdf(
        f"{PDF_DIR}/shoprite_edited.pdf", new_master_path
    )
    update_master(parsed_items, new_master_path)
    master_info = import_master_info_from_csv(new_master_path)
    assert len(master_info) > 1
    assert master_info["3082"]["Name"] == "Fresh Broccoli"
