import pytest

from app.services.document_parser import DocumentParseError, extract_text_from_bytes


def test_extract_txt():
    text = extract_text_from_bytes("note.txt", b"Hello world, this is a claim.")
    assert "Hello world" in text


def test_extract_unsupported_type_raises():
    with pytest.raises(DocumentParseError):
        extract_text_from_bytes("file.exe", b"binary junk")


def test_extract_empty_txt_raises():
    with pytest.raises(DocumentParseError):
        extract_text_from_bytes("empty.txt", b"   ")
