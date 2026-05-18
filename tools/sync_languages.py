#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

from languages import ALL_LANGS, LANGUAGES, NAV_TEXT, TARGET_LANGS

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / "tools" / ".translation-cache.json"
HTML_FILES = [ROOT / "index.html"] + sorted((ROOT / "posts").glob("*.html"))


def load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def translate_batch(texts: list[str], target: str, cache: dict[str, str]) -> list[str]:
    out: list[str] = []
    for text in texts:
        key = f"en:{target}:{text}"
        if key in cache:
            out.append(cache[key])
            continue

        query = urllib.parse.urlencode(
            [("client", "gtx"), ("sl", "en"), ("tl", target), ("dt", "t"), ("q", text)]
        )
        url = f"https://translate.googleapis.com/translate_a/single?{query}"
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))
                translated = "".join(part[0] for part in data[0] if part and part[0])
                cache[key] = translated
                break
            except Exception as exc:  # noqa: BLE001 - retry external translation service
                last_error = exc
                time.sleep(1.5 * (attempt + 1))
        else:
            raise RuntimeError(f"Translation failed for {target}: {last_error}")
        out.append(cache[key])
        time.sleep(0.05)
    return out


def clone_lang_blocks(soup: BeautifulSoup, cache: dict[str, str]) -> bool:
    changed = False
    source_nodes = list(soup.select(".lang-en"))
    for source in source_nodes:
        parent = source.parent
        if not parent:
            continue
        existing = {
            cls.removeprefix("lang-")
            for child in parent.find_all(recursive=False)
            for cls in (child.get("class") or [])
            if cls.startswith("lang-")
        }
        insertion_point = source
        for lang in TARGET_LANGS:
            if lang in existing:
                continue
            clone = BeautifulSoup(str(source), "html.parser").find()
            classes = [c for c in clone.get("class", []) if not c.startswith("lang-")]
            clone["class"] = classes + [f"lang-{lang}"]
            translate_clone_contents(clone, lang, cache)
            insertion_point.insert_after(clone)
            insertion_point = clone
            existing.add(lang)
            changed = True
    return changed


def replace_contents(tag, html_fragment: str) -> None:
    fragment = BeautifulSoup(html_fragment, "html.parser")
    tag.clear()
    for item in list(fragment.contents):
        tag.append(item)


def translate_clone_contents(clone, lang: str, cache: dict[str, str]) -> None:
    source_html = clone.decode_contents()
    if not source_html.strip():
        return
    if len(source_html) <= 700:
        replace_contents(clone, translate_batch([source_html], lang, cache)[0])
        return

    for child in list(clone.find_all(recursive=False)):
        child_html = child.decode_contents()
        if not child_html.strip():
            continue
        if len(child_html) <= 700:
            replace_contents(child, translate_batch([child_html], lang, cache)[0])
        else:
            for node in list(child.descendants):
                if isinstance(node, NavigableString) and node.strip():
                    node.replace_with(translate_batch([str(node)], lang, cache)[0])


def replace_language_control(soup: BeautifulSoup) -> bool:
    changed = False
    controls = soup.select("#lang-toggle")
    for control in controls:
        if control.name == "select":
            continue
        select = soup.new_tag("select", id="lang-toggle")
        select["class"] = "lang-switch-btn"
        select["aria-label"] = "Language"
        for code, meta in LANGUAGES.items():
            option = soup.new_tag("option", value=code)
            option.string = meta["label"]
            select.append(option)
        control.replace_with(select)
        changed = True
    return changed


def fix_known_ui_labels(soup: BeautifulSoup) -> bool:
    changed = False
    english_to_group = {
        values["en"]: values for values in NAV_TEXT.values()
    }
    for source in soup.select(".lang-en"):
        key = source.get_text(" ", strip=True)
        values = english_to_group.get(key)
        if not values or not source.parent:
            continue
        for child in source.parent.find_all(recursive=False):
            for cls in child.get("class", []):
                if cls.startswith("lang-"):
                    lang = cls.removeprefix("lang-")
                    if lang in values and child.get_text(" ", strip=True) != values[lang]:
                        child.clear()
                        child.append(values[lang])
                        changed = True
    return changed


def add_language_script(soup: BeautifulSoup, is_post: bool) -> bool:
    src = "../language.js" if is_post else "language.js"
    for script in soup.find_all("script", src=src):
        return False
    body = soup.body
    if not body:
        return False
    script = soup.new_tag("script", src=src)
    first_inline = body.find("script")
    if first_inline:
        first_inline.insert_before(script)
    else:
        body.append(script)
    return True


def replace_post_inline_script(soup: BeautifulSoup) -> bool:
    scripts = [s for s in soup.find_all("script") if not s.get("src")]
    if not scripts:
        return False
    script = scripts[-1]
    script.string = """
        document.addEventListener('DOMContentLoaded', () => {
            const mobileBtn = document.querySelector('.mobile-menu-btn');
            const nav = document.querySelector('.main-nav');
            if (mobileBtn && nav) {
                mobileBtn.addEventListener('click', () => {
                    nav.classList.toggle('active');
                    mobileBtn.classList.toggle('active');
                });
            }
        });
    """
    return True


def sync_html_file(path: Path, cache: dict[str, str]) -> bool:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    changed = False
    changed |= replace_language_control(soup)
    changed |= clone_lang_blocks(soup, cache)
    changed |= fix_known_ui_labels(soup)
    is_post = path.parent.name == "posts"
    if is_post:
        changed |= replace_post_inline_script(soup)
    changed |= add_language_script(soup, is_post)
    if changed:
        path.write_text(str(soup), encoding="utf-8")
    return changed


def translate_js_reports(cache: dict[str, str]) -> bool:
    path = ROOT / "script.js"
    text = path.read_text(encoding="utf-8")
    changed = False

    def enrich_object(match: re.Match[str]) -> str:
        nonlocal changed
        block = match.group(0)
        title_match = re.search(r'title_en:\s*"((?:\\.|[^"])*)"', block)
        excerpt_match = re.search(r'excerpt_en:\s*"((?:\\.|[^"])*)"', block)
        if not title_match or not excerpt_match:
            return block
        title = bytes(title_match.group(1), "utf-8").decode("unicode_escape")
        excerpt = bytes(excerpt_match.group(1), "utf-8").decode("unicode_escape")
        insert_after = excerpt_match.end()
        additions = []
        for lang in TARGET_LANGS:
            if f"title_{lang}:" in block and f"excerpt_{lang}:" in block:
                continue
            t_title = translate_batch([title], lang, cache)[0]
            t_excerpt = translate_batch([excerpt], lang, cache)[0]
            additions.append(
                f',\n            title_{lang}: "{escape_js(t_title)}",'
                f'\n            excerpt_{lang}: "{escape_js(t_excerpt)}"'
            )
        if additions:
            changed = True
            block = block[:insert_after] + "".join(additions) + block[insert_after:]
        return block

    text = re.sub(r"\{\n\s*title_zh:.*?\n\s*url:\s*\"[^\"]+\"\n\s*\}", enrich_object, text, flags=re.S)
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def escape_js(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def main() -> None:
    cache = load_cache()
    changed_files = []
    for path in HTML_FILES:
        print(f"Syncing {path.relative_to(ROOT).as_posix()}...", flush=True)
        if sync_html_file(path, cache):
            changed_files.append(path.relative_to(ROOT).as_posix())
            save_cache(cache)
    print("Syncing script.js report metadata...", flush=True)
    if translate_js_reports(cache):
        changed_files.append("script.js")
    save_cache(cache)
    print("Updated:")
    for item in changed_files:
        print(f"- {item}")
    print(f"Translation cache entries: {len(cache)}")


if __name__ == "__main__":
    main()
