const SITE_LANGUAGES = [
    { code: "zh", label: "中文", html: "zh-Hant" },
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

function setSiteLanguage(lang) {
    const selected = SITE_LANGUAGES.find((item) => item.code === lang) || SITE_LANGUAGES[0];
    document.body.setAttribute("data-lang", selected.code);
    document.documentElement.setAttribute("lang", selected.html);
    localStorage.setItem("lang", selected.code);

    const control = document.getElementById("lang-toggle");
    if (control) {
        control.value = selected.code;
    }
}

window.setSiteLanguage = setSiteLanguage;

document.addEventListener("DOMContentLoaded", () => {
    const control = document.getElementById("lang-toggle");
    if (control && !control.dataset.initialized) {
        control.dataset.initialized = "true";
        control.addEventListener("change", () => setSiteLanguage(control.value));
    }

    const saved = localStorage.getItem("lang") || "zh";
    setSiteLanguage(saved);
});
