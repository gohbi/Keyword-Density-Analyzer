import pytest
from pathlib import Path

from ..utils import read_file, preprocess, keyword_density


@pytest.fixture
def sample_txt(tmp_path):
    # Create a tiny txt file (pdfminer can read plain text too)
    p = tmp_path / "sample.txt"
    p.write_text("Python is great. Python developers love Python.")
    return str(p)


def test_preprocess():
    text = "Python developers love Python."
    tokens = preprocess(text)
    assert "python" in tokens
    assert "developer" in tokens  # lemmatized
    assert "love" in tokens
    # stop‑words like "is" should be gone
    assert "is" not in tokens


def test_keyword_density():
    tokens = ["python", "python", "developer", "love", "python"]
    dens = keyword_density(tokens)
    # Expect python to be first with count 3
    assert dens[0][0] == "python"
    assert dens[0][1] == 3
    assert dens[0][2] == pytest.approx(60.0)  # 3/5 * 100


def test_read_file_pdf(tmp_path):
    # Create a tiny PDF using pdfminer‑compatible text
    pdf_path = tmp_path / "tiny.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer <<>>\n%%EOF")
    # pdfminer will raise an error for a malformed PDF; we just ensure the function
    # raises a ValueError for unsupported types (here we treat it as unsupported)
    with pytest.raises(ValueError):
        read_file(str(pdf_path))
