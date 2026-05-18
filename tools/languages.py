LANGUAGES = {
    "zh": {"label": "中文", "html": "zh-Hant", "source": "zh"},
    "en": {"label": "English", "html": "en", "source": "en"},
    "ja": {"label": "日本語", "html": "ja", "source": "en"},
    "ko": {"label": "한국어", "html": "ko", "source": "en"},
    "es": {"label": "Español", "html": "es", "source": "en"},
    "de": {"label": "Deutsch", "html": "de", "source": "en"},
    "fr": {"label": "Français", "html": "fr", "source": "en"},
    "no": {"label": "Norsk", "html": "no", "source": "en"},
    "nl": {"label": "Nederlands", "html": "nl", "source": "en"},
    "it": {"label": "Italiano", "html": "it", "source": "en"},
}

TARGET_LANGS = [code for code in LANGUAGES if code not in ("zh", "en")]
ALL_LANGS = list(LANGUAGES)

NAV_TEXT = {
    "home": {
        "zh": "首頁", "en": "Home", "ja": "ホーム", "ko": "홈", "es": "Inicio",
        "de": "Start", "fr": "Accueil", "no": "Hjem", "nl": "Home", "it": "Home",
    },
    "about": {
        "zh": "關於我們", "en": "About", "ja": "私たちについて", "ko": "소개", "es": "Acerca de",
        "de": "Über uns", "fr": "À propos", "no": "Om oss", "nl": "Over ons", "it": "Chi siamo",
    },
    "history": {
        "zh": "歷史真相", "en": "History", "ja": "歴史", "ko": "역사", "es": "Historia",
        "de": "Geschichte", "fr": "Histoire", "no": "Historie", "nl": "Geschiedenis", "it": "Storia",
    },
    "reports": {
        "zh": "人權報告", "en": "Reports", "ja": "報告", "ko": "보고서", "es": "Informes",
        "de": "Berichte", "fr": "Rapports", "no": "Rapporter", "nl": "Rapporten", "it": "Rapporti",
    },
    "contact": {
        "zh": "聯絡我們", "en": "Contact", "ja": "連絡先", "ko": "연락처", "es": "Contacto",
        "de": "Kontakt", "fr": "Contact", "no": "Kontakt", "nl": "Contact", "it": "Contatto",
    },
    "back_reports": {
        "zh": "← 返回報告列表", "en": "← Back to Reports", "ja": "← 報告一覧に戻る",
        "ko": "← 보고서 목록으로 돌아가기", "es": "← Volver a informes",
        "de": "← Zurück zu den Berichten", "fr": "← Retour aux rapports",
        "no": "← Tilbake til rapportene", "nl": "← Terug naar rapporten",
        "it": "← Torna ai rapporti",
    },
    "read_more": {
        "zh": "閱讀全文 →", "en": "Read More →", "ja": "続きを読む →", "ko": "더 읽기 →",
        "es": "Leer más →", "de": "Weiterlesen →", "fr": "Lire la suite →",
        "no": "Les mer →", "nl": "Lees verder →", "it": "Leggi di più →",
    },
}
