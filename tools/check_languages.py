#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

from languages import ALL_LANGS

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [ROOT / "index.html"] + sorted((ROOT / "posts").glob("*.html"))


def main() -> int:
    failures: list[str] = []
    for path in HTML_FILES:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        classes = {
            cls.removeprefix("lang-")
            for tag in soup.find_all(class_=re.compile(r"\blang-"))
            for cls in tag.get("class", [])
            if cls.startswith("lang-")
        }
        missing = [lang for lang in ALL_LANGS if lang not in classes]
        if missing:
            failures.append(f"{path.relative_to(ROOT)} missing: {', '.join(missing)}")

        for tag in soup.select(".lang-en"):
            parent = tag.parent
            if not parent:
                continue
            sibling_langs = {
                cls.removeprefix("lang-")
                for child in parent.find_all(recursive=False)
                for cls in (child.get("class") or [])
                if cls.startswith("lang-")
            }
            missing_siblings = [lang for lang in ALL_LANGS if lang not in sibling_langs]
            if missing_siblings:
                failures.append(
                    f"{path.relative_to(ROOT)} incomplete sibling set near '{tag.get_text(' ', strip=True)[:60]}': "
                    + ", ".join(missing_siblings)
                )

    script_text = (ROOT / "script.js").read_text(encoding="utf-8")
    for lang in ALL_LANGS:
        if f"title_{lang}" not in script_text or f"excerpt_{lang}" not in script_text:
            failures.append(f"script.js missing report fields for {lang}")

    if failures:
        print("Language check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Language check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
