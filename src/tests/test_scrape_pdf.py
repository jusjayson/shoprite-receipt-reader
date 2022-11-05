PDF_DIR = "./tests/test_data"

from pdf_scraper import (
    clean_full_txt,
    get_full_txt_from_pdf,
    get_parsed_items_from_pdf,
    get_raw_items_from_pdf,
)


def remove_spaces_and_lines(word):
    return word.replace(" ", "").replace("\n", "")


def test_remove_prefix():
    prefix_phrases = ("Your digital receipt", "ananomus@gmail.com", "Dear ANAN OMUS")
    full_txt = get_full_txt_from_pdf(f"{PDF_DIR}/shoprite_edited.pdf")
    assert all(prefix_phrase in full_txt for prefix_phrase in prefix_phrases)

    full_txt = clean_full_txt(full_txt)
    assert not any(prefix_phrase in full_txt for prefix_phrase in prefix_phrases)


def test_remove_suffix():
    suffix_phrases = (
        "ONLINE PAYMENT $221.80",
        "SHOPRITE OF ANONVYLLE",
        "This e-mail was sent to",
    )
    full_txt = get_full_txt_from_pdf(f"{PDF_DIR}/shoprite_edited.pdf")
    assert all(suffix_phrase in full_txt for suffix_phrase in suffix_phrases)

    full_txt = clean_full_txt(full_txt)
    assert not any(suffix_phrase in full_txt for suffix_phrase in suffix_phrases)


def test_remove_gmail_pattern():
    full_txt = get_full_txt_from_pdf(f"{PDF_DIR}/shoprite_edited.pdf")
    assert "gmail" in full_txt
    assert "https://mail.google.com" in full_txt
    full_txt = clean_full_txt(full_txt)
    assert "gmail" not in full_txt
    assert "https://mail.google.com" not in full_txt


def test_get_single_raw_item():
    raw_item = get_raw_items_from_pdf(f"{PDF_DIR}/shoprite_edited_one_item.pdf")[0]
    assert remove_spaces_and_lines("BROC CRWNS RPC") in remove_spaces_and_lines(
        raw_item[0]
    )
    assert remove_spaces_and_lines("3082") in remove_spaces_and_lines(raw_item[1])
    assert remove_spaces_and_lines("1 x $6.41") in remove_spaces_and_lines(raw_item[2])
    assert remove_spaces_and_lines("Price: $1.99/lb") in remove_spaces_and_lines(
        raw_item[4]
    )
    assert remove_spaces_and_lines("Qty: 3.22lb") in remove_spaces_and_lines(
        raw_item[5]
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
        raw_item_two[4]
    )


def test_get_one_item_per_page():
    raw_items = get_raw_items_from_pdf(f"{PDF_DIR}/shoprite_edited_one_item_per_pg.pdf")
    raw_item_one, raw_item_two, raw_item_three = raw_items
    assert remove_spaces_and_lines("BROC CRWNS RPC") in remove_spaces_and_lines(
        raw_item_one[0]
    )
    assert remove_spaces_and_lines("1 x $6.41") in remove_spaces_and_lines(
        raw_item_one[2]
    )

    assert remove_spaces_and_lines("PEPPE GREEN RPC 22") in remove_spaces_and_lines(
        raw_item_two[0]
    )
    assert remove_spaces_and_lines("1 x $2.18") in remove_spaces_and_lines(
        raw_item_two[2]
    )

    assert remove_spaces_and_lines("REY PARCHMENT PAPE") in remove_spaces_and_lines(
        raw_item_three[0]
    )
    assert remove_spaces_and_lines("1090074331") in remove_spaces_and_lines(
        raw_item_three[1]
    )
    assert remove_spaces_and_lines("1 x $3.79") in remove_spaces_and_lines(
        raw_item_three[2]
    )


def test_coupon_code():
    raw_item = get_raw_items_from_pdf(f"{PDF_DIR}/shoprite_edited.pdf")[2]
    assert remove_spaces_and_lines(
        "**SC**Green Peppers: $0.72"
    ) in remove_spaces_and_lines(raw_item[3])


def test_across_page():
    raw_items = get_raw_items_from_pdf(
        f"{PDF_DIR}/shoprite_edited_item_across_page.pdf"
    )
    raw_item = raw_items[0]

    assert remove_spaces_and_lines("PEPPER HABANERO 10") in remove_spaces_and_lines(
        raw_item[0]
    )
    assert remove_spaces_and_lines("3125") in remove_spaces_and_lines(raw_item[1])
    assert remove_spaces_and_lines("1 x $0.30") in remove_spaces_and_lines(raw_item[2])
    assert remove_spaces_and_lines("Price: $6.00/lb") in remove_spaces_and_lines(
        raw_item[4]
    )
    assert remove_spaces_and_lines("Qty: 0.05lb") in remove_spaces_and_lines(
        raw_item[5]
    )


def test_get_parsed_single_item():
    parsed_item = get_parsed_items_from_pdf(
        f"{PDF_DIR}/shoprite_edited_one_item_per_pg.pdf"
    )[1]
    assert parsed_item == {
        "Name": "PEPPE GREEN RPC 22",
        "SKU": "4065",
        "Price per quantity": "1 x $2.18",
        "Price per unit": "$1.49/lb",
        "Quantity": "1.46lb",
        "Cat": None,
    }
