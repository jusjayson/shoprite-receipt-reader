PDF_DIR = "./tests/test_data"

from pdf_scraper import get_raw_items_from_pdf


def remove_spaces_and_lines(word):
    return word.replace(" ", "").replace("\n", "")


def test_get_single_raw_item():
    raw_item = get_raw_items_from_pdf(f"{PDF_DIR}/shoprite_edited_one_item.pdf")[0]
    assert remove_spaces_and_lines("BROC CRWNS RPC") in remove_spaces_and_lines(
        raw_item[0]
    )
    assert remove_spaces_and_lines("3082") in remove_spaces_and_lines(raw_item[1])
    assert remove_spaces_and_lines("1 x $6.41") in remove_spaces_and_lines(raw_item[2])
    assert remove_spaces_and_lines("Price: $1.99/lb") in remove_spaces_and_lines(
        raw_item[3]
    )
    assert remove_spaces_and_lines("Qty: 3.22lb") in remove_spaces_and_lines(
        raw_item[4]
    )


def test_get_raw_items_on_single_page():
    raw_items = get_raw_items_from_pdf(f"{PDF_DIR}/shoprite_edited_one_pg_items.pdf")
    raw_item_one, raw_item_two = raw_items
    assert remove_spaces_and_lines("BROC CRWNS RPC") in remove_spaces_and_lines(
        raw_item_one[0]
    )
    assert remove_spaces_and_lines("1 x $6.41") in remove_spaces_and_lines(
        raw_item_one[2]
    )

    assert remove_spaces_and_lines("PEPPER HABANERO 10") in remove_spaces_and_lines(
        raw_item_two[0]
    )
    assert remove_spaces_and_lines("3125") in remove_spaces_and_lines(raw_item_two[1])
    assert remove_spaces_and_lines("1 x $0.30") in remove_spaces_and_lines(
        raw_item_two[2]
    )
    assert remove_spaces_and_lines("Price: $6.00/lb") in remove_spaces_and_lines(
        raw_item_two[3]
    )
