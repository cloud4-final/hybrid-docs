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


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--require-page-id", action="store_true")
    args = parser.parse_args(argv)
    errors = [e for f in args.files for e in check_doc(Path(f), args.require_page_id)]
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
