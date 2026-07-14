#!/usr/bin/env python3
"""Read-only audit of multilingual publication completeness.

This command never translates or writes content.  It reports missing language
containers, inconsistent localized structures, and missing report-card fields.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from languages import ALL_LANGS


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT_PAGES = (
    "index.html",
    "about.html",
    "contact.html",
    "privacy.html",
    "protests.html",
    "reports.html",
    "sources.html",
    "terms.html",
    "404.html",
)


def public_html_files() -> tuple[Path, ...]:
    roots = tuple(ROOT / name for name in PUBLIC_ROOT_PAGES if (ROOT / name).exists())
    posts = tuple(sorted(path for path in (ROOT / "posts").glob("*.html") if path.name != "template.html"))
    return roots + posts


def localized_container(soup: BeautifulSoup, lang: str):
    return soup.select_one(f'[data-language-body="{lang}"]') or soup.select_one(
        f".article-body.lang-{lang}"
    )


def structure_signature(container) -> tuple:
    """Describe direct publication structure without comparing translated text."""
    return tuple(
        (
            child.name,
            child.get("data-section", ""),
            len(child.find_all(["h1", "h2", "h3"])),
        )
        for child in container.find_all(recursive=False)
        if getattr(child, "name", None) not in {"script", "style"}
    )


def html_audit() -> tuple[list[str], list[str]]:
    missing: list[str] = []
    inconsistent: list[str] = []
    for path in public_html_files():
        relative = path.relative_to(ROOT).as_posix()
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        containers = {lang: localized_container(soup, lang) for lang in ALL_LANGS}

        if any(containers.values()):
            absent = [lang for lang, node in containers.items() if node is None]
            if absent:
                missing.append(f"{relative}: missing language containers {', '.join(absent)}")
                continue
            signatures = {lang: structure_signature(node) for lang, node in containers.items()}
            reference = signatures[ALL_LANGS[0]]
            mismatched = [lang for lang in ALL_LANGS[1:] if signatures[lang] != reference]
            if mismatched:
                inconsistent.append(
                    f"{relative}: localized structure differs for {', '.join(mismatched)}"
                )
            continue

        counts = {lang: len(soup.select(f".lang-{lang}")) for lang in ALL_LANGS}
        absent = [lang for lang, count in counts.items() if count == 0]
        if absent:
            missing.append(f"{relative}: missing language containers {', '.join(absent)}")
        elif len(set(counts.values())) != 1:
            inconsistent.append(
                f"{relative}: localized element counts differ "
                + ", ".join(f"{lang}={counts[lang]}" for lang in ALL_LANGS)
            )
    return missing, inconsistent


def report_card_audit() -> list[str]:
    path = ROOT / "script.js"
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    expected_posts = sorted(
        item.name for item in (ROOT / "posts").glob("*.html") if item.name != "template.html"
    )
    for name in expected_posts:
        pattern = re.compile(
            r'\{[^{}]*?url:\s*"posts/' + re.escape(name) + r'"[^{}]*?\}', re.S
        )
        match = pattern.search(text)
        if not match:
            issues.append(f"script.js: missing report card for posts/{name}")
            continue
        card = match.group(0)
        for lang in ALL_LANGS:
            for field in ("title", "excerpt"):
                value = re.search(rf'{field}_{lang}:\s*"([^"]*)"', card)
                if not value or not value.group(1).strip():
                    issues.append(f"script.js: posts/{name} missing {field}_{lang}")
    return issues


def audit() -> dict[str, list[str]]:
    missing, inconsistent = html_audit()
    return {
        "missing_language_containers": missing,
        "missing_report_card_fields": report_card_audit(),
        "inconsistent_language_structures": inconsistent,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only audit of ten-language HTML and report-card completeness."
    )
    parser.add_argument("--json", action="store_true", help="print the audit as JSON")
    args = parser.parse_args()
    results = audit()

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for heading, entries in results.items():
            print(f"{heading}: {len(entries)}")
            for entry in entries:
                print(f"- {entry}")

    issue_count = sum(len(entries) for entries in results.values())
    if issue_count:
        print(f"Read-only language audit failed with {issue_count} issue(s).")
        return 1
    print("Read-only language audit passed; no files were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
