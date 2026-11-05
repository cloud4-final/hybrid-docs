import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bootstrap_confluence as b  # noqa: E402


def test_plan_pages_titles_and_order():
    assert b.plan_pages() == [
        ("", "0. 공통 기준"),
        ("contracts.md", "공통 기준 · 파트 간 계약"),
        ("decisions.md", "공통 기준 · 결정 기록"),
    ]


def test_child_titles_match_markdown_h1():
    root = Path(__file__).resolve().parents[3]
    for doc, title in b.CHILDREN:
        first_heading = next(l for l in (root / doc).read_text(encoding="utf-8").splitlines() if l.startswith("# "))
        assert first_heading == f"# {title}"
