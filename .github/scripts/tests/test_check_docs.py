import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_docs  # noqa: E402


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_rejects_unmasked_ipv4():
    found = check_docs.find_unmasked_ipv4("원본은 10.11.0.130이다. 입구 54.1.2.3")
    assert found == ["10.11.0.130", "54.1.2.3"]


def test_allows_masked_and_allowlist():
    text = "10.11.x.130, 54.116.x.x, DNS 1.1.1.1, Tailscale 100.64.0.0/10"
    assert check_docs.find_unmasked_ipv4(text) == []


def test_page_id_required_only_with_flag(tmp_path):
    path = write(tmp_path, "contracts.md", "# T\n")
    assert check_docs.check_doc(path, require_page_id=False) == []
    errors = check_docs.check_doc(path, require_page_id=True)
    assert any("confluence-page-id" in e for e in errors)


def test_page_id_present_passes(tmp_path):
    path = write(tmp_path, "contracts.md", "<!-- confluence-page-id: 123 -->\n# T\n")
    assert check_docs.check_doc(path, require_page_id=True) == []


def test_main_reports_unmasked_ip(tmp_path, capsys):
    path = write(tmp_path, "decisions.md", "주소 10.10.0.110\n")
    assert check_docs.main([str(path)]) == 1
    assert "10.10.0.110" in capsys.readouterr().out


def test_main_ok(tmp_path):
    path = write(tmp_path, "decisions.md", "주소 10.10.x.110\n")
    assert check_docs.main([str(path)]) == 0
