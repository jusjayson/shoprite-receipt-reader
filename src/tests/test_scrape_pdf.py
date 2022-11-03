PDF_DIR = "./test_data/"

from pdf_scraper import get_raw_items_from_pdf


def remove_spaces_and_lines(word):
    return word.replace(" ", "").replace("\n", "")


def test_get_single_raw_item():
    raw_items = get_raw_items_from_pdf(f"{PDF_DIR}/shporite_edited_one_item.pdf")
    assert remove_spaces_and_lines("BROC CRWNS RPC") in remove_spaces_and_lines(
        raw_items[0]
    )
    assert remove_spaces_and_lines("3082") in remove_spaces_and_lines(raw_items[1])
    assert remove_spaces_and_lines("1 x $6.41") in remove_spaces_and_lines(raw_items[2])
    assert remove_spaces_and_lines("Price: $1.99/lb") in remove_spaces_and_lines(
        raw_items[3]
    )
    assert remove_spaces_and_lines("Qty: 3.22lb") in remove_spaces_and_lines(
        raw_items[4]
    )
