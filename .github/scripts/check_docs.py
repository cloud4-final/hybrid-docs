"""hybrid-docs 문서 검사: 가리지 않은 IPv4와 Confluence page ID."""
import argparse
import re
import sys
from pathlib import Path

IPV4 = re.compile(r"(?<![\d.])\d{1,3}(?:\.\d{1,3}){3}(?![\d.])")
ALLOWED_IPV4 = {"1.1.1.1", "100.64.0.0"}
PAGE_ID = re.compile(r"<!-- confluence-page-id: \d+ -->")


def find_unmasked_ipv4(text: str) -> list[str]:
    return [ip for ip in IPV4.findall(text) if ip not in ALLOWED_IPV4]


def check_doc(path: Path, require_page_id: bool) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = [
        f"{path}: 가리지 않은 IP {ip} (앞 두 자리만 쓰고 나머지는 x로 가린다)"
        for ip in find_unmasked_ipv4(text)
    ]
    if require_page_id and not PAGE_ID.search(text):
        errors.append(f"{path}: <!-- confluence-page-id: N --> 주석이 없다")
    return errors


HEADING = re.compile(r"^### (\S+) · ", re.M)
ID_FORMAT = re.compile(r"^([CAM]-[A-Z]+-\d{3}|D-\d{8}-\d{2})$")
ID_REF = re.compile(r"\b(?:[CAM]-[A-Z]+-\d{3}|D-\d{8}-\d{2})\b")
FIELD = re.compile(r"^- ([a-z_]+):", re.M)
STATUSES = ("active", "open", "superseded")
REQUIRED = {
    "C": {"active": ["rule", "scope", "violation", "source"], "open": ["rule", "owner"], "superseded": ["rule", "by"]},
    "D": {"active": ["decision", "implies", "why", "scope", "source"], "superseded": ["decision", "by"]},
    "A": {"active": ["rule", "scope", "violation", "source"], "superseded": ["rule", "by"]},
    "M": {"active": ["rule", "owner", "scope", "source"], "open": ["rule", "owner"], "superseded": ["rule", "by"]},
}


def parse_blocks(text: str) -> list[tuple[str, dict[str, str]]]:
    """'### ID · 제목' 블록을 (ID, {field: value}) 목록으로 나눈다."""
    starts = [m for m in HEADING.finditer(text)]
    blocks = []
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        body = text[m.end():end].split("\n## ")[0]
        fields = {}
        for f in FIELD.finditer(body):
            line_end = body.find("\n", f.end())
            fields[f.group(1)] = body[f.end():line_end if line_end != -1 else None].strip()
        blocks.append((m.group(1), fields))
    return blocks


def check_blocks(paths: list[Path]) -> list[str]:
    errors, seen, texts = [], {}, []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        texts.append(text)
        for block_id, fields in parse_blocks(text):
            where = f"{path.name}:{block_id}"
            if not ID_FORMAT.match(block_id):
                errors.append(f"{where}: ID 형식이 C-AAA-000 또는 D-YYYYMMDD-00이 아니다")
                continue
            if block_id in seen:
                errors.append(f"{where}: ID 중복 ({seen[block_id]})")
            seen[block_id] = path.name
            status = fields.get("status", "").split(" ")[0]
            if status not in STATUSES or status not in REQUIRED[block_id[0]]:
                errors.append(f"{where}: status는 {', '.join(REQUIRED[block_id[0]])} 중 하나여야 한다")
                continue
            for name in REQUIRED[block_id[0]][status]:
                if not fields.get(name):
                    errors.append(f"{where}: 필드 {name}가 없다")
    for text in texts:
        for ref in sorted(set(ID_REF.findall(text)) - set(seen)):
            errors.append(f"존재하지 않는 ID 참조: {ref}")
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--require-page-id", action="store_true")
    parser.add_argument("--blocks", action="store_true", help="규칙·결정 블록 형식 검사")
    args = parser.parse_args(argv)
    errors = [e for f in args.files for e in check_doc(Path(f), args.require_page_id)]
    if args.blocks:
        errors += check_blocks([Path(f) for f in args.files])
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
