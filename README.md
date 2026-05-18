# zhonghuafreedom.github.io

## Multilingual content workflow

The site now keeps each article synchronized across:

- Chinese, English, Japanese, Korean, Spanish, German, French, Norwegian, Dutch, and Italian

When adding or editing article content, update the Chinese and English source text first, then run:

```bash
python3 tools/sync_languages.py
python3 tools/check_languages.py
```

`tools/sync_languages.py` uses the English blocks as the source for Japanese, Korean, Spanish, German, French, Norwegian, Dutch, and Italian. `tools/check_languages.py` verifies that pages and report cards include all required languages before committing.
