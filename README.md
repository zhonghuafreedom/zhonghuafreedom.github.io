# zhonghuafreedom.github.io

## Multilingual editorial workflow

Traditional Chinese is the content master for this site. English, Japanese, Korean, Spanish, German, French, Norwegian, Dutch, and Italian must each be translated by a person and reviewed fact by fact. Existing human translations must never be overwritten by machine-translated English, and network translation services must not be used to produce publication content.

When an article changes, update all ten language versions together. Verify the facts, source attribution, uncertainty and attribution wording, timeline, article title and deck, and the corresponding homepage report-card title and excerpt in every language. A script run is not evidence that editorial translation is complete.

`tools/sync_languages.py` is a read-only missing-item audit. It reports absent language containers, absent `script.js` `title_*` and `excerpt_*` fields, and inconsistent language structures. It never translates or writes HTML, JavaScript, or cache files.

Run the complete release checks from the repository root:

```bash
python3 tools/check_languages.py
python3 tools/check_languages.py --matrix
python3 tools/check_languages.py --self-test
node --check script.js
node --check language.js
node --check protests.js
git diff --check
```

## Repository and preview copy

`/Users/darrianlong/Downloads/zhonghuafreedom` is the deployment repository. `/Users/darrianlong/Desktop/zhonghuafreedom 2` is a local preview copy. Make and validate changes in the deployment repository first, then copy only the files approved for the current maintenance task and verify them byte for byte.

Do not commit, push, or change remote repository settings unless the maintainer explicitly authorizes those actions.
