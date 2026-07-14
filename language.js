const SITE_LANGUAGES = [
    { code: "zh", label: "繁體中文", html: "zh-Hant" },
    { code: "en", label: "English", html: "en" },
    { code: "ja", label: "日本語", html: "ja" },
    { code: "ko", label: "한국어", html: "ko" },
    { code: "es", label: "Español", html: "es" },
    { code: "de", label: "Deutsch", html: "de" },
    { code: "fr", label: "Français", html: "fr" },
    { code: "no", label: "Norsk", html: "no" },
    { code: "nl", label: "Nederlands", html: "nl" },
    { code: "it", label: "Italiano", html: "it" },
];

const INTERFACE_LABELS = {
    menu: {
        zh: "切換導覽選單", en: "Toggle navigation", ja: "ナビゲーションを切り替える", ko: "탐색 메뉴 전환",
        es: "Alternar navegación", de: "Navigation umschalten", fr: "Afficher ou masquer la navigation",
        no: "Vis eller skjul navigasjon", nl: "Navigatie openen of sluiten", it: "Apri o chiudi la navigazione",
    },
    navigation: {
        zh: "主要導覽", en: "Main navigation", ja: "メインナビゲーション", ko: "주요 탐색",
        es: "Navegación principal", de: "Hauptnavigation", fr: "Navigation principale",
        no: "Hovednavigasjon", nl: "Hoofdnavigatie", it: "Navigazione principale",
    },
    language: {
        zh: "選擇語言", en: "Select language", ja: "言語を選択", ko: "언어 선택",
        es: "Seleccionar idioma", de: "Sprache auswählen", fr: "Choisir la langue",
        no: "Velg språk", nl: "Taal kiezen", it: "Seleziona la lingua",
    },
    logo: {
        zh: "中華自由陣線標誌", en: "Chinese Liberty Front logo", ja: "中華自由戦線のロゴ", ko: "중화자유전선 로고",
        es: "Logotipo del Frente Chino por la Libertad", de: "Logo der Chinesischen Freiheitsfront",
        fr: "Logo du Front chinois pour la liberté", no: "Logo for Kinesisk frihetsfront",
        nl: "Logo van het Chinees Vrijheidsfront", it: "Logo del Fronte Cinese per la Libertà",
    },
};

function safeReadLanguage() {
    try {
        return window.localStorage.getItem("lang");
    } catch (_error) {
        return null;
    }
}

function safeWriteLanguage(lang) {
    try {
        window.localStorage.setItem("lang", lang);
    } catch (_error) {
        // The interface still changes for the current page when storage is unavailable.
    }
}

function updateLocalizedAttributes(lang) {
    document.querySelectorAll("[data-i18n-aria]").forEach((node) => {
        const key = node.dataset.i18nAria;
        const value = INTERFACE_LABELS[key]?.[lang];
        if (value) node.setAttribute("aria-label", value);
    });
    document.querySelectorAll("[data-i18n-alt]").forEach((node) => {
        const key = node.dataset.i18nAlt;
        const value = INTERFACE_LABELS[key]?.[lang];
        if (value) node.setAttribute("alt", value);
    });
}

function localizedDocumentTitle(lang) {
    const key = `title${lang.charAt(0).toUpperCase()}${lang.slice(1)}`;
    return document.body?.dataset[key] || null;
}

function setSiteLanguage(lang, options = {}) {
    const selected = SITE_LANGUAGES.find((item) => item.code === lang) || SITE_LANGUAGES[0];
    const persist = options.persist !== false;
    document.body.setAttribute("data-lang", selected.code);
    document.documentElement.setAttribute("lang", selected.html);
    if (persist) safeWriteLanguage(selected.code);

    const control = document.getElementById("lang-toggle");
    if (control) control.value = selected.code;
    updateLocalizedAttributes(selected.code);
    const title = localizedDocumentTitle(selected.code);
    if (title) document.title = title;

    document.dispatchEvent(new CustomEvent("site-language-change", {
        detail: { language: selected.code },
    }));
    return selected.code;
}

window.setSiteLanguage = setSiteLanguage;
window.SITE_LANGUAGES = SITE_LANGUAGES;

document.addEventListener("DOMContentLoaded", () => {
    const control = document.getElementById("lang-toggle");
    if (control && !control.dataset.initialized) {
        control.dataset.initialized = "true";
        control.addEventListener("change", () => setSiteLanguage(control.value));
    }
    const saved = safeReadLanguage();
    const initial = SITE_LANGUAGES.some((item) => item.code === saved) ? saved : "zh";
    setSiteLanguage(initial, { persist: Boolean(saved) });
});
