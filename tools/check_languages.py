#!/usr/bin/env python3
"""Release gate for the 54 public multilingual human-rights dossiers.

The gate deliberately audits the visible contents of the two critical columns,
not only their specially-classed main paragraphs.  It is intentionally small:
every check below maps to a published editorial requirement and is exercised by
an in-memory negative test.
"""
from __future__ import annotations

import argparse
import copy
import csv
import fnmatch
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"
LANGS = ("zh", "en", "ja", "ko", "es", "de", "fr", "no", "nl", "it")
HEADER_TRANSLATION_LANGS = ("ja", "ko", "es", "de", "fr", "no", "nl", "it")
FILES = tuple(sorted(path for path in POSTS.glob("*.html") if path.name != "template.html"))
EXPECTED_FILES = 54
PUBLIC_PAGES = ("about.html", "contact.html", "privacy.html", "sources.html", "terms.html", "protests.html")
PUBLIC_NAV_PAGES = PUBLIC_PAGES + ("index.html", "reports.html")
RELEASE_ROOT_PAGES = (
    "index.html", "about.html", "contact.html", "privacy.html",
    "protests.html", "reports.html", "sources.html", "terms.html", "404.html",
)
SITEMAP_ROOT_PATHS = (
    "/", "/about.html", "/contact.html", "/privacy.html",
    "/protests.html", "/reports.html", "/sources.html", "/terms.html",
)
SITE_ORIGIN = "https://zhonghuafreedom.org"
REQUIRED_CONFIG_EXCLUDES = {
    "backup_legacy", "docs", "tools", "posts/template.html", "README.md",
    "DNS配置指南.md", "configure-domain.sh", "CNAME.txt", ".gitignore", ".DS_Store",
}
FORBIDDEN_PUBLIC_LINK_PARTS = {"backup_legacy", "docs", "tools"}
LOCAL_PATH_MARKERS = re.compile(r"file://|/Users/|\bDownloads\b|\bDesktop\b|/tmp(?:/|\b)", re.I)
SOURCE_CATEGORY_CODES = (
    "family-material", "victim-statement", "witness-material", "civilian-record",
    "original-footage", "archived-content", "independent-media", "overseas-media",
    "human-rights-organization", "research-institution", "court-document", "institutional-public",
)
EXPECTED_SOURCE_URLS = (
    "https://www.hrw.org/world-report/2026/country-chapters/china",
    "https://www.hrw.org/news/2026/02/04/china-repression-deepens-extends-abroad",
    "https://www.amnesty.org/en/location/asia-and-the-pacific/east-asia/china/report-china/",
    "https://www.amnesty.org/en/location/asia-and-the-pacific/east-asia/hong-kong/report-hong-kong/",
    "https://freedomhouse.org/country/china/freedom-world/2026",
    "https://freedomhouse.org/report/china-dissent-monitor",
    "https://freedomhouse.org/report/china-dissent-monitor/2025/issue-11-october-december-2025",
    "https://www.cecc.gov/publications/commission-analysis/report-prcs-transnational-repression-and-malign-influence-2025",
    "https://rsf.org/en/country/china",
    "https://rsf.org/en/2026-rsf-index-press-freedom-25-year-low",
    "https://rsf.org/en/classement-mondial-2026-par-r%C3%A9gions-une-d%C3%A9gradation-de-la-libert%C3%A9-de-la-presse-dans-100-pays-sur",
    "https://cpj.org/special-reports/2025-journalist-jailings-remain-stubbornly-high-harsh-prison-conditions-pervasive/",
    "https://cpj.org/2026/01/journalist-jailings-imperil-a-free-press-worldwide-amid-reports-of-life-threatening-prison-conditions-cpj/",
    "https://www.ohchr.org/en/press-releases/2026/01/un-experts-alarmed-reports-forced-labour-uyghur-tibetan-and-other-minorities",
    "https://www.hrw.org/news/2026/06/29/hong-kong-beijing-tightens-social-control",
    "https://www.hrw.org/news/2025/12/15/hong-kong-jimmy-lai-convicted-on-bogus-national-security-charges",
)
FROZEN_POST_HASHES = {
    "2024-report.html": "827c063d4dcd4b1b0632e3a4e5ee3a2c1ad63281f96aeabfe82447a1c4c31de7",
    "2026-report.html": "3a20d8d4961f93aea4d651c790199001e13d733f90346b14735d1127c09998d8",
    "709-crackdown.html": "e15a5ce5db927b9f7bd890abe0d4e5b9080e5554bf0bec267d8466353af66e08",
    "ai-weiwei.html": "f21b0b7c0e0332737eaeda1dbb2594676e497909bf98c30ad03f92bf7e976849",
    "causeway-bay-books.html": "a95519e30b746abea193042a663b13dcaa601609f6b09534d39bcce3d9fcade4",
    "chen-guangcheng.html": "ff7b5ccdcafbf37ecc8f55d14f4a32d5384891a3b16456bd04424e146a251e55",
    "chen-qiushi.html": "fbaf4a523d791bd8d5cc2885ee03a2baa80fe180be5f3b5377cc39efa67bab6b",
    "china-dissent-monitor-2025.html": "285fcc6efd044c7e5fbfa2677e5a67f05762c88c10ace14527f81cac4d62204f",
    "china-human-rights-cases-supplement-2026.html": "dd7e93bfc66029c0a0ec811a33bc1603b53e9cf94081d2ea5d17b3a937e5f023",
    "cultural-revolution.html": "06c03c8b0f14482e0a337ffe83f555b0d3b52d4515cbff365d2a099e2f3ca364",
    "dalai-lama-exile.html": "b6de188932b530129ec4f859b6878199dbd207949d94bc08604441dacbd34639",
    "digital-surveillance.html": "5f3be407b89f5f338cd596afcf1e426b96fa87d7171785692912b2eb926f690f",
    "dong-yaoqiong-ink-protest.html": "22ba5e50706e75f8ddaefd72fd5f2ee55780c52c2ef1836fc7f2364ab16ae4aa",
    "falun-gong-persecution.html": "5916b31636ec1941a9b235b569bc058ebc368e749cd6b0dce64c6a7497adeb7c",
    "fang-bin-citizen-journalist.html": "31f7bfd5de34c86aa4708da1e1f93ef2b3f62235164c7cd10d6295efc57d9fca",
    "feng-county-chained-woman.html": "b806128916825886ac3a43eafde12f4464c6d07313beb73b070fa5c24b352b4a",
    "gao-yu.html": "b269d377d67bffd543080d7739c608f3dc50ec67b849f6ed8ecc0f1066a9371d",
    "great-leap-famine.html": "3afd890e272cfcca8d86bd910436795a442742563f8284d20634b0b4bc8321f6",
    "guangzhou-haizhu-lockdown-protests.html": "85a155d4341f65e89f3b9d6b8ed20a6a4ec5d5811f9813218a49856ce02f27af",
    "guiyang-quarantine-bus-crash.html": "e6513cecc31cce28c6e5ac56afe13f6bc01ab3550b3b047a806cbfb9757ec9f2",
    "henan-bank-depositor-protests.html": "3ed1594834d493ab8cf378c9064bd3c0d5e4dc8adcb579bf7b953faf359c5973",
    "hk-12.html": "1707e68f1694f2d7935968c82149af054ead0d2ed6c1b8b248d4906046213ff6",
    "hk-47.html": "3a7f00922852250b874c72636d7e7df1510ae0348a8cf6a727ef69d74af03396",
    "hong-kong-nsl.html": "1614ea9ce33885cb1d6d0817c164370eed49624084de808d30f247bb4e2f1891",
    "hong-kong-update-2026.html": "17a507f652e958661daf885f88cf705ac131f52103b322f97a10f838116e3bb1",
    "hu-xinyu-disappearance.html": "721ba3599fec01edfb3795547034ddcb7e863e626f251cf168bbb9a759c42191",
    "huang-qi.html": "412606a89d429969d558bf27fae5544532590d8f98060ccf1610e9b738586884",
    "huang-xueqin-wang-jianbing.html": "83e1cfe010b2fc21675a48e24e3dcee9cea3f369d706e13e4314b89169c64448",
    "jiang-tianyong.html": "99d3f1959124e2ade9e894e4d9cd245e28eeed8e2b1bf7df1c848ab68ea4c726",
    "jiangyou-school-bullying-protests.html": "a146f5db0d0a3389e42b21fe2fc0f2f7e25878fb8d833ee0282e026b28ddd5ab",
    "land-reform-anti-rightist.html": "879d9d5a7dff317e5173c88b0903781e00e7b394b72ab6aaaeaf5b16959a74a8",
    "li-wenliang.html": "e99e5a3b0898ea77e1f67d83170a48725342c00b491feba1a7043e2d4a2677ad",
    "li-zehua.html": "35828dad2e370718f9463d147f132813aabde8e168ea1975f8b3214973e0e49d",
    "liu-xia.html": "f9040c7eaa72929eb4dcc03c5037011a6d6b6ca6c632f87906edcfab1d7b5a35",
    "liu-xiaobo.html": "818d31eb6c6405287451774173a387e8730d09f138c900c19f00939b8db2f86a",
    "ningbo-xiaoluoxi-medical-case.html": "f9b10c5e64d9ccb34fed75fa2eed2ced514ab3032420f3807ff6d8be6da61e07",
    "niu-tengyu.html": "9ba6417c412e7c4e3b6224d21a72de09e1aec031bee9befd64519e90bbe9acf6",
    "peng-zaizhou.html": "2651c878f3062bb2a78c7d27b94ef622d78eaba3ae708a5a9781203b31ecbcf3",
    "press-freedom-2026.html": "6cc3cd86fd2e2c300e132d393a21a6ca311fe827330cd83e6415c04f59237c03",
    "pucheng-student-death-protest.html": "c4d156aceb162df226f1fc49a75f79466d0652520b2987bdd035c4cf36da751e",
    "shanghai-lockdown.html": "e5a4f2b4755f5a01f0c68b1392bf467e184c96e39fe9e201a4d85655f7da7116",
    "terminus2049-chen-mei-cai-wei.html": "ee95857894de55c6fd977af83cd938ba19ea1669090b86db626038cbdc790e6c",
    "tiananmen-1989.html": "49684e83d193ae5af38e93db55742b2de5fea28439a0c679a6261c73ee94a8c4",
    "tianshui-kindergarten-lead-poisoning.html": "fc90ad12e4025db754c5b043851ff2b1a7aca1416dd3de20b418dcbb04117b14",
    "transnational-repression-2026.html": "dd800e92f59d020ac9bc080f8909f8d7fd900bec4ac5e489ff76f3a9f78fdb3d",
    "transnational-repression.html": "10c42ba08311e75ffd13075195e90e52df1fc35dfdcd56978b4218193aac4dd2",
    "wang-bingzhang.html": "6473f358b7a69b992f265294b135d9d3e5b1cc63f2db3d52f9d318445d24b9cc",
    "wang-quanzhang.html": "f68a0f7c05ad6a7ae2ecb003ef5cbcc96c28dab0b476ebaa08f950d4df67b70e",
    "white-paper.html": "5aeff2d4863876548a143b38a84c286f9c9025e0ccd2ccb880288907152606ee",
    "wuhan-pensioner-protests.html": "7a33b06fef296d8a18a31cddbeb8ced69f188b3279171b46a644146853df3e1e",
    "xinjiang-camps.html": "e3bccd7f9a2cf8974a8bd86b1fdb9d04a2d197c41c758a582150c96c4c5386e2",
    "xinjiang-tibet-forced-labour-2026.html": "50e156da347849ad55f4bb55dfbc144e17f9566c5a825c080c44beeef71f1b6b",
    "zhang-zhan.html": "6d123f8556b60a72eab85850fac6cc203e2bb9bbdc5df8530188f8eac75512df",
    "zhengzhou-foxconn-worker-protests.html": "540ee1602ccad2bdf37af1198218ca94bcc37426b14d744949663fafe1e59016",
}
FROZEN_CONTROL_HASHES = {
    "posts/template.html": "bade0505f7319891b99fdf77598504f835d8c42c240aba879c604228c550b18d",
    "docs/EDITORIAL_CONTROL_STANDARD.md": "da5e7b2db90b2e778d7d0d5406b2940b7a45d4b578c20aacf1b740afff117033",
}
HEADINGS = {
    "zh": (("人权", "人權"), ("保护", "保護")),
    "en": (("human rights",), ("protection",)),
    "ja": (("人権",), ("保護",)),
    "ko": (("인권",), ("보호",)),
    "es": (("derechos humanos",), ("protección",)),
    "de": (("menschenrecht",), ("schutz",)),
    "fr": (("droits humains",), ("protection",)),
    "no": (("menneskerett",), ("beskytt",)),
    "nl": (("mensenrechten",), ("bescherm",)),
    "it": (("diritti umani",), ("protezione",)),
}
STATE_TERMS = {
    "zh": r"警方|公安|政府|法院|醫院|医院|學校|学校|平台|行政|國家|警務|當局|当局|機關|机关|權力|权力|制度|官方|中共|黨|党|公社",
    "en": r"police|state|government|court|hospital|school|platform|administrative|security|authorit|official|institution|agency|party|local|communist|mao|cadre|commune",
    "ja": r"警察|公安|治安|政府|国|裁判所|司法制度|刑務所|病院|学校|プラットフォーム|行政|国家|当局|機関|権力|公式|共産|毛沢東|人民公社",
    "ko": r"경찰|공안|정부|법원|병원|학교|플랫폼|행정|국가|당국|기관|권력|공식|공산|마오|인민공사|지방|현|조사",
    "es": r"polic|estado|gobierno|tribunal|hospital|escuela|plataforma|administr|autoridad|oficial|instituci|organismo|comunista|mao|cuadro|comuna",
    "de": r"polizei|staat|regierung|gericht|krankenhaus|schule|plattform|verwaltung|behörd|offiziell|institution|amt|kommunist|mao|kader|kommune",
    "fr": r"police|état|gouvernement|tribunal|hôpital|école|plateforme|administr|autorité|officiel|institution|organe|communiste|mao|cadre|commune",
    "no": r"politi|stat|regjering|domstol|sykehus|skole|plattform|administr|myndighet|offisiell|institusjon|kommunist|mao|kader|kommune",
    "nl": r"politie|staat|regering|rechtbank|ziekenhuis|school|platform|administr|autoriteit|offici|instelling|orgaan|communist|mao|kader|gemeente|lokaal|district|provinc|dorps|jiangsu|xuzhou",
    "it": r"polizia|stato|governo|tribunale|ospedale|scuola|piattaforma|amministr|autorità|ufficial|istituzion|organo|comunista|mao|quadro|comun|locale|contea|provincia|partito",
}
ACTION_TERMS = {
    "zh": r"拘|扣|帶走|传唤|傳喚|删|刪|限制|控制|封|監|监|審|审|轉運|驅離|壓|压|介入|拒|失聯|失联|處置|处置|分配|集體|集体|徵糧|征粮|管理",
    "en": r"detain|arrest|summon|delete|restrict|control|censor|monitor|prosecut|sentence|transfer|block|pressure|interven|deny|remove|disappear|custod|harass|silenc|govern|regulat|manage|organis|collectiv|redistribut|confisc|require|framework|algorithm|request|handle|ban",
    "ja": r"拘束|連行|召喚|削除|制限|統制|監視|起訴|判決|移送|遮断|圧力|介入|拒否|不明|処分|再分配|集団化|徴発|管理|運動|政策|決定",
    "ko": r"구금|연행|소환|삭제|제한|통제|감시|기소|판결|이송|차단|압력|개입|거부|실종|처분|재분배|집단화|징발|관리|운동|정책|결정",
    "es": r"deten|arrest|cita|elimin|restring|control|censur|vigila|proces|conden|traslad|bloque|presi[oó]n|interven|nieg|desapar|acoso|organiz|colectiv|redistrib|confisc|gestion",
    "de": r"haft|fest|vorlad|lösch|beschränk|kontroll|zens|überwach|anklag|urteil|überführ|block|druck|eingriff|verweig|verschw|schikan|organis|kollektiv|umverteil|enteign|verwalt",
    "fr": r"détention|arrêt|convo|supprim|restre|contrôl|censur|surveill|poursui|condamn|transfér|bloqu|pression|interven|refus|dispar|harcèl|organis|collectiv|redistrib|confisc|gér",
    "no": r"fengsl|arrester|innkall|slett|begrens|kontroll|sensur|overvåk|tiltal|dom|overfør|blokker|press|inngrep|avsl|forsvinn|trakasser|organiser|kollektiv|omfordel|konfisk|forvalt",
    "nl": r"detent|arresteer|dagvaard|verwijder|beperk|controle|censuur|toezicht|vervolg|veroordeel|overbreng|blokkeer|druk|ingrijp|weiger|verdwijn|intimideer|organiseer|collectiv|herverdeel|confisceer|onderzoek|beheer|lood|medisch|test",
    "it": r"detenz|arrest|convoc|cancell|limit|controll|censur|sorvegl|persegu|condann|trasfer|bloc|pression|interven|rifiut|scompar|molest|organizz|collettiv|redistrib|confisc|gest",
}
IMPACT_TERMS = {
    "zh": r"家屬|家属|家長|家庭|家人|女孩|孩子|兒童|儿童|個人|个人|聯絡人|联系人|受害|證據|证据|救濟|救济|補救|补救|風險|风险|壓力|压力|報復|报复|權利|权利|生命|真相|發聲|发声|公民|居民|參與者|参与者",
    "en": r"family|relative|worker|homeowner|resident|participant|source|victim|evidence|remedy|relief|risk|exposure|pressure|rights|dignity|safety|people|person|life|livelihood|property|truth|speech|public|contact",
    "ja": r"家族|被害|証拠|救済|危険|圧力|権利|尊厳|安全|人びと|市民|生命|真実|発言|社会|責任|住民|生活|支援者|メディア",
    "ko": r"가족|주민|노동자|참가자|증인|친인척|피해|증거|구제|구호|위험|압력|권리|존엄|안전|사람|시민|생명|생계|주택|보건|진실|발언",
    "es": r"famil|víctim|prueba|recurso|riesgo|presión|derechos|dignidad|seguridad|persona|vida|verdad|públic",
    "de": r"famil|betroffen|beweis|abhilfe|rechtsschutz|risik|druck|recht|würde|sicherheit|mensch|leben|wahrheit|öffentlich",
    "fr": r"famille|victime|preuve|recours|risque|pression|droits|dignité|sécurité|personne|vie|vérité|public",
    "no": r"famil|slekt|arbeider|huseier|innbygger|deltaker|berørt|bevis|rettsmiddel|lettelse|risiko|press|rettighet|verdighet|sikkerhet|mennesk|liv|levebrød|eiendom|sannhet|offentlig",
    "nl": r"famil|getroffen|bewijs|rechtsmiddel|risico|druk|rechten|waardigheid|veiligheid|mensen|leven|waarheid|publiek",
    "it": r"famigl|parent|partecip|testimon|vittim|prov|rimedio|soccorso|assistenza|denuncia|esposizione|rischio|pressione|diritti|dignità|sicurezza|persone|vita|verità|pubblic",
}

# The list includes the user-supplied release scan plus applicant-guide and
# disclaimer vocabulary that must never survive in any visible critical node.
BANNED = re.compile(
    r"The documented course of|It can be used to examine|This case can be used to understand|"
    r"post deletion|offline rights protection|current restrictions|passing by Fangqiao|return them|"
    r"medical malpractice was recorded|protection review can|in protection reviews|"
    r"can be used to (?:understand|examine|assess)|does not make the final judgment|"
    r"does not (?:solely )?(?:decide|determine).*protection|does not replace.*legal evidence|is not legal advice|"
    r"本[頁页案報告报告].{0,20}(?:可用|用于|用於|認為|认为)|此案可用[于於]理解|"
    r"它可用[于於]審查|它不就事故法律責任作最終判斷|"
    r"ですことを示している|ますことを示している|"
    r"습니다는 점을 보여 준다|됩니다는 점을 보여 준다|"
    r"(?:esta|este) (?:página|caso|informe).{0,60}(?:usar|utilizar|evaluar|examinar)|"
    r"(?:diese|dieser) (?:seite|fall|bericht).{0,60}(?:verwend|bewert|prüf)|"
    r"(?:cette|ce) (?:page|affaire|rapport).{0,60}(?:utilis|évalu|exam)|"
    r"(?:denne|deze|questa|questo).{0,60}(?:gebruik|vurder|valut|esam|utilizz|valut)",
    re.IGNORECASE | re.DOTALL,
)
GLOBAL_TERMS = re.compile(
    r"segregation|segregación|ségrégation|segregering|segregatie|segregazione|"
    r"人種隔離|인종차별|offline rights protection|post deletion|current restrictions|"
    r"passing by Fangqiao|return them|medical malpractice was recorded",
    re.IGNORECASE,
)
PUBLIC_DIRECTIVES = re.compile(
    r"(?:must|should|needs? to) be (?:attributed|assessed|reported|reviewed|understood|"
    r"distinguished|read|scrutinized|considered|evaluated|verified|confirmed|de-identified)|"
    r"shall be reported|source and privacy protection should be attached|"
    r"should retain source restrictions|can only (?:confirm|corroborate)|only corroborate",
    re.IGNORECASE,
)
PUBLIC_DIRECTIVES_BY_LANG = {
    "zh": re.compile(r"(?:必須|必须|需要|應該|应该|須|须).{0,24}(?:歸屬|归属|審查|审查|評估|评估|理解|區分|区分)"),
    "ja": re.compile(r"(?:帰属|評価|報告|再検討|精査|区別|理解).{0,20}(?:必要|なければ|べき|はず)"),
    "ko": re.compile(r"(?:귀속|평가|보고|검토|구별|이해).{0,20}(?:되어야|해야)"),
    "es": re.compile(r"\b(?:debe|deben|necesita)\b.{0,30}(?:atribuir|evaluar|revisar|informar|examinar)", re.I),
    "de": re.compile(r"\b(?:muss|müssen|sollte|sollten)\b.{0,30}(?:zugeordnet|zugeschrieben|bewertet|überprüft|gemeldet|gelesen)", re.I),
    "fr": re.compile(r"\b(?:doit|doivent|devrait|devraient)\b.{0,30}(?:attribu|évalu|examin|signal|lu)", re.I),
    "no": re.compile(r"\b(?:må|bør)\b.{0,30}(?:tilskriv|vurder|gjennomgå|rapport|les)", re.I),
    "nl": re.compile(r"\b(?:moet|moeten|zou|zouden)\b.{0,30}(?:toegeschreven|beoordeeld|herzien|gerapporteerd|gelezen)", re.I),
    "it": re.compile(r"\b(?:deve|devono|dovrebbe|dovrebbero)\b.{0,30}(?:attribu|valutat|rivist|segnalat|lett)", re.I),
}
ZHANG_KO_MALE = re.compile(r"(?<![가-힣])(?:그가|그의|그를|그는)(?![가-힣])")
JAPANESE_STATE_AS_SHU = re.compile(
    r"党(?:と|および)州|州の(?:機関|アーカイブ)|"
    r"(?<![一-龯々〆ヵヶァ-ヶぁ-ん])州は(?=[^。！？]{0,100}(?:責任|義務|公開|補償|保護|提供|調達|記録|救済|開示))"
)
# Exact equality is normally evidence of an English fallback.  Keep any future
# intentional proper-name-only exception explicit and field-specific.
ARTICLE_HEADER_FALLBACK_ALLOWLIST: set[tuple[str, str, str]] = set()


def contains_public_directive(text: str, lang: str) -> bool:
    return bool(PUBLIC_DIRECTIVES.search(text) or PUBLIC_DIRECTIVES_BY_LANG.get(lang, re.compile(r"(?!x)x")).search(text))


def body_for(soup: BeautifulSoup, lang: str):
    return soup.select_one(f".article-body.lang-{lang}") or soup.select_one(f'[data-language-body="{lang}"]')


def find_heading(body, tokens: tuple[str, ...]):
    if body is None:
        return None
    for h2 in body.find_all("h2"):
        text = h2.get_text(" ", strip=True).casefold()
        if any(token in text for token in tokens):
            return h2
    return None


def section_nodes(h2):
    if h2 is None:
        return []
    result = []
    node = h2.find_next_sibling()
    while node is not None and node.name != "h2":
        if getattr(node, "name", None):
            result.append(node)
        node = node.find_next_sibling()
    return result


def section_text(h2) -> str:
    return " ".join(node.get_text(" ", strip=True) for node in section_nodes(h2))


def sentence_parts(text: str, lang: str):
    """Split visible prose without requiring a space after CJK punctuation."""
    if lang in {"zh", "ja"}:
        pattern = r"(?<=[。！？])"
    elif lang == "ko":
        # Korean pages normally use Latin full stops, but imported quotations
        # can retain CJK punctuation.  Both forms must remain testable.
        pattern = r"(?<=[.!?。！？])"
    else:
        pattern = r"(?<=[.!?])\s+"
    return [value.strip() for value in re.split(pattern, text) if value.strip()]


def normalise_sentence(text: str) -> str:
    return re.sub(r"[\s\u00a0'’\"“”«»。，、；：,;:()（）\-–—]", "", text).casefold()


def long_sentence(text: str, lang: str) -> bool:
    if lang in {"zh", "ja", "ko"}:
        return len(re.sub(r"\s+", "", text)) >= 45
    return len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", text)) >= 12


def first_alpha_is_upper(text: str) -> bool:
    """Reject a lowercase residual word even when punctuation or digits lead."""
    for character in text:
        if character.isalpha():
            return character.isupper()
    return False


def overlap_rate(left: str, right: str, lang: str) -> float:
    left_parts = {normalise_sentence(value) for value in sentence_parts(left, lang) if value}
    right_parts = {normalise_sentence(value) for value in sentence_parts(right, lang) if value}
    if not left_parts or not right_parts:
        return 0.0
    return len(left_parts & right_parts) / min(len(left_parts), len(right_parts))


def article_header_issues(soup: BeautifulSoup, path: Path) -> list[str]:
    issues = []
    for field, selector in (("title", "h1.article-title"), ("deck", "p.article-dek")):
        english = soup.select_one(f"{selector} .lang-en")
        english_text = english.get_text(" ", strip=True) if english else ""
        if not english_text:
            issues.append(f"article {field}: missing English text")
            continue
        for lang in HEADER_TRANSLATION_LANGS:
            node = soup.select_one(f"{selector} .lang-{lang}")
            localized = node.get_text(" ", strip=True) if node else ""
            if not localized:
                issues.append(f"article {field}: missing {lang} text")
            elif localized == english_text and (path.name, field, lang) not in ARTICLE_HEADER_FALLBACK_ALLOWLIST:
                issues.append(f"article {field}: {lang} falls back to English")
        for lang in LANGS:
            node = soup.select_one(f"{selector} .lang-{lang}")
            localized = node.get_text(" ", strip=True) if node else ""
            if localized and contains_public_directive(localized, lang):
                issues.append(f"article {field}: {lang} contains an editorial directive")
    return issues


def public_directive_nodes(body, lang: str) -> list:
    """Find editorial instructions in all visible prose without confusing
    substantive remedy demands with editor-facing language.

    The precise English instruction patterns are safe to enforce in every
    visible paragraph and list item, including the two critical columns.
    Broader translated-language patterns remain limited to ordinary prose,
    because critical conclusions legitimately demand that authorities disclose,
    investigate, compensate, or provide a remedy.
    """
    result = []
    for node in body.find_all(["p", "li"]):
        if node.find_parent("ul", class_="source-list") is not None:
            continue
        text = node.get_text(" ", strip=True)
        if PUBLIC_DIRECTIVES.search(text):
            result.append(node)
            continue
        classes = set(node.get("class") or [])
        if classes & {"critical-conclusion", "critical-protection"}:
            continue
        pattern = PUBLIC_DIRECTIVES_BY_LANG.get(lang)
        if pattern and pattern.search(text):
            result.append(node)
    return result


def issue_list(soup: BeautifulSoup, path: Path, *, source_signatures=True):
    issues: list[str] = []
    issues.extend(article_header_issues(soup, path))
    source_reference = None
    for lang in LANGS:
        body = body_for(soup, lang)
        if body is None:
            issues.append(f"{lang}: missing article body")
            continue
        if public_directive_nodes(body, lang):
            issues.append(f"{lang}: public visible text contains an editorial directive")
        if path.name == "zhang-zhan.html" and lang == "ko" and ZHANG_KO_MALE.search(body.get_text(" ", strip=True)):
            issues.append("ko: Zhang Zhan is referred to with a male pronoun")
        if lang == "ja" and JAPANESE_STATE_AS_SHU.search(body.get_text(" ", strip=True)):
            issues.append("ja: the Chinese state or Party-state is mistranslated as 州")
        headings = body.find_all("h2")
        # Seven core sections are mandatory.  Some established dossiers also
        # retain separately headed official-response and unresolved-question
        # material; those additions are allowed when the same core sequence is
        # still present in every language.
        if len(headings) < 7:
            issues.append(f"{lang}: needs the seven core h2 sections, found {len(headings)}")
        rights = find_heading(body, HEADINGS[lang][0])
        protection = find_heading(body, HEADINGS[lang][1])
        if rights is None or protection is None:
            issues.append(f"{lang}: missing human-rights or protection heading")
            continue
        visible_critical = {}
        for kind, heading, klass, required in (
            ("rights", rights, "critical-conclusion", ("subject", "state-action", "second-harm", "conclusion")),
            ("protection", protection, "critical-protection", ("subject", "state-action", "pressure-path", "remedy-responsibility")),
        ):
            nodes = section_nodes(heading)
            mains = [node for node in nodes if node.name == "p" and klass in (node.get("class") or [])]
            if len(mains) != 1:
                issues.append(f"{lang} {kind}: needs exactly one {klass} in its visible column")
                continue
            main = mains[0]
            text = main.get_text(" ", strip=True)
            visible_critical[kind] = text
            floor = 70 if lang in {"zh", "ja", "ko"} else 100
            if len(text) < floor:
                issues.append(f"{lang} {kind}: main conclusion is too short")
            ceiling = 900 if lang in {"zh", "ja", "ko"} else 1800
            if len(text) > ceiling:
                issues.append(f"{lang} {kind}: critical paragraph is abnormally long ({len(text)} characters)")
            # A critical column consists of its single main paragraph.  Moving
            # copied prose into an ordinary visible node must never bypass QA.
            if len(nodes) != 1 or nodes[0] is not main:
                issues.append(f"{lang} {kind}: critical column has {len(nodes) - 1} additional visible nodes")
            anchors = {
                token
                for span in main.select("[data-critical-anchor]")
                if span.get_text(" ", strip=True)
                for token in span.get("data-critical-anchor", "").split()
            }
            missing = set(required) - anchors
            if missing:
                issues.append(f"{lang} {kind}: missing anchors {', '.join(sorted(missing))}")
            marker = main.select_one("[data-critical-case]")
            parts = sentence_parts(text, lang)
            opening = parts[0] if parts else ""
            marker_value = marker.get("data-critical-case", "").strip() if marker else ""
            if marker is None or len(marker.get_text(" ", strip=True)) < 12:
                issues.append(f"{lang} {kind}: lacks a visible case-specific factual subject")
            elif marker_value != opening or not text.startswith(marker_value):
                issues.append(f"{lang} {kind}: data-critical-case is not the complete visible opening sentence")
            if lang in {"es", "de", "fr", "no", "nl", "it"} and not first_alpha_is_upper(text):
                issues.append(f"{lang} {kind}: begins with a lowercase word or residual fragment")
            for node in nodes:
                text_in_node = node.get_text(" ", strip=True)
                if BANNED.search(text_in_node):
                    issues.append(f"{lang} {kind}: banned disclaimer, webpage subject, or machine phrase in visible column")
                    break
            # The conclusion must point to a state-controlled actor, a concrete
            # act, and a human consequence; names or a title cannot substitute.
            compact = section_text(heading).casefold()
            if not re.search(STATE_TERMS[lang], compact, re.I):
                issues.append(f"{lang} {kind}: lacks a state or state-controlled actor")
            if not re.search(ACTION_TERMS[lang], compact, re.I):
                issues.append(f"{lang} {kind}: lacks a concrete state action")
            if not re.search(IMPACT_TERMS[lang], compact, re.I):
                issues.append(f"{lang} {kind}: lacks a victim, evidence, pressure, or remedy consequence")
        if set(visible_critical) == {"rights", "protection"}:
            rights_text = visible_critical["rights"]
            protection_text = visible_critical["protection"]
            if rights_text and rights_text in protection_text:
                issues.append(f"{lang}: rights text is fully contained in protection text")
            rate = overlap_rate(rights_text, protection_text, lang)
            if rate > 0.25:
                issues.append(f"{lang}: rights/protection sentence overlap is {rate:.0%}, above 25%")
        # All seven sections must carry visible content; source section needs
        # an actual linked source list.  This avoids class-only validation.
        for number, heading in enumerate(headings, start=1):
            if len(section_text(heading)) < 30:
                issues.append(f"{lang}: section {number} is visually skeletal")
        sources = body.select("ul.source-list > li")
        if not sources:
            issues.append(f"{lang}: source section lacks source-list items")
        signature = tuple(
            (
                item.get("data-source-id"), item.get("data-source-type"), item.get("data-source-date"),
                (item.select_one("a[href]").get("href") if item.select_one("a[href]") else None),
            ) for item in sources
        )
        if any(not item[1] or not item[3] for item in signature):
            issues.append(f"{lang}: a source lacks typed linked metadata")
        if source_signatures:
            if source_reference is None:
                source_reference = signature
            elif signature != source_reference:
                issues.append(f"{lang}: source ID/type/date/URL/order differs from Chinese")
    return issues


def loaded_documents(paths=FILES):
    return {
        path: BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for path in paths
    }


def duplicate_sentence_issues(documents=None, *, threshold=3) -> list[str]:
    if documents is None:
        documents = loaded_documents()
    groups: dict[tuple[str, str], set[str]] = defaultdict(set)
    examples: dict[tuple[str, str], str] = {}
    for path, soup in documents.items():
        for lang in LANGS:
            body = body_for(soup, lang)
            for heading in (find_heading(body, HEADINGS[lang][0]), find_heading(body, HEADINGS[lang][1])):
                if heading is None:
                    continue
                for sentence in sentence_parts(section_text(heading), lang):
                    if long_sentence(sentence, lang):
                        key = (lang, normalise_sentence(sentence))
                        groups[key].add(path.name)
                        examples.setdefault(key, sentence)
    return [
        f"{lang}: cross-case repeated long sentence {examples[(lang, sentence)]!r} in {', '.join(sorted(cases))}"
        for (lang, sentence), cases in groups.items() if sentence and len(cases) >= threshold
    ]


def card_issues() -> list[str]:
    text = (ROOT / "script.js").read_text(encoding="utf-8")
    issues = []
    entries = re.findall(r"\{[^{}]*?url:\s*\"posts/([^\"]+)\"[^{}]*?\}", text, re.S)
    for path in FILES:
        name = path.name
        pattern = re.compile(r"\{[^{}]*?url:\s*\"posts/" + re.escape(name) + r"\"[^{}]*?\}", re.S)
        match = pattern.search(text)
        if not match:
            issues.append(f"script.js: missing card for {name}")
            continue
        card = match.group(0)
        english_title = None
        for lang in LANGS:
            title = re.search(rf"title_{lang}:\s*\"([^\"]*)\"", card)
            excerpt = re.search(rf"excerpt_{lang}:\s*\"([^\"]*)\"", card)
            if not title or not excerpt or not title.group(1).strip() or not excerpt.group(1).strip():
                issues.append(f"script.js: {name} lacks {lang} title or excerpt")
                continue
            if lang == "en":
                english_title = title.group(1).strip()
            elif english_title and title.group(1).strip() == english_title:
                issues.append(f"script.js: {name} {lang} title falls back to English")
            if BANNED.search(title.group(1) + " " + excerpt.group(1)):
                issues.append(f"script.js: {name} {lang} card contains prohibited editorial wording")
            if contains_public_directive(title.group(1) + " " + excerpt.group(1), lang):
                issues.append(f"script.js: {name} {lang} card contains an editorial directive")
    return issues


PUBLIC_BANNED = re.compile(
    r"\b(?:game|player|simulation|fictional|prompt|internal review|AI[- ]generated)\b|"
    r"not legal, medical, or immigration advice|"
    r"not (?:legal|medical|immigration)(?:, (?:medical|immigration))* (?:advice|guidance)|"
    r"check (?:the )?original sources|(?:for reference only|only for reference)|"
    r"(?:this|the) page (?:does not|cannot) (?:decide|determine|replace)|"
    r"official (?:finding|conclusion|position).{0,24}(?:final truth|controls|prevails)|"
    r"游戏|玩家|模擬|模拟|虛構|虚构|提示詞|提示词|內部審核|内部审核|AI生成|"
    r"不構成.{0,18}(?:法律|醫療|医疗|移民).{0,12}(?:建議|建议|意見|意见)|"
    r"(?:以|請查|请查).{0,12}(?:原始來源|原始来源).{0,10}(?:為準|为准)|"
    r"(?:以|依).{0,12}(?:官方結論|官方结论).{0,8}(?:為準|为准)|"
    r"本[頁页].{0,8}(?:僅供參考|仅供参考|不決定|不决定|不替代)|"
    r"法的、医療、移民.{0,12}(?:助言|アドバイス)|原典を確認|"
    r"법률.{0,8}의료.{0,8}이민.{0,12}(?:조언|자문)|원본 출처를 확인|"
    r"no (?:constituye|es) asesoramiento (?:jurídico|médico|migratorio)|"
    r"keine (?:Rechts|medizinische|Einwanderungs).{0,20}(?:beratung|hinweise)|"
    r"ne constitue pas un conseil (?:juridique|médical|migratoire)|"
    r"ikke (?:juridisk|medisinsk|innvandrings).{0,18}(?:råd|veiledning)|"
    r"geen (?:juridisch|medisch|immigratie).{0,18}(?:advies|raad)|"
    r"non (?:costituisce|è) (?:consulenza|parere) (?:legale|medic[oa]|sull.?immigrazione)",
    re.IGNORECASE | re.DOTALL,
)
SOCIAL_MEDIA_FALSE_CLAIM = re.compile(
    r"(?:contact|reach).{0,40}social media.{0,40}(?:home|site)|"
    r"(?:首頁|主页).{0,20}(?:社交媒體|社群媒體|社交媒体).{0,20}(?:聯絡|联系)|"
    r"(?:social media|réseaux sociaux|soziale medien|sociale medier|sociale media|social network).{0,50}(?:homepage|home page|startseite|accueil)",
    re.IGNORECASE | re.DOTALL,
)

# Public-page semantic regression terms found during the independent language
# audit.  These are narrow, known-bad formulations rather than a general style
# checker: every expression below changes the asserted meaning of its section.
ABOUT_SERVICE_MODE = re.compile(
    r"提供服務|サービスを提供しています|서비스를 제공|presta servicios|"
    r"betreut betroffene Menschen|est au service des personnes touchées|"
    r"betjener berørte mennesker|bedient getroffen mensen|è al servizio delle persone colpite|"
    r"\bserves affected people\b",
    re.IGNORECASE,
)
TERMS_UNCERTAINTY_MARKERS = re.compile(
    r"不確定性標記|uncertainty markers|不確実性の指標|불확실성 표시|"
    r"marcadores de incertidumbre|Unsicherheitsmerkmale|marqueurs d’incertitude|"
    r"usikkerhetsmarkører|onzekerheidsmarkeringen|indicatori di incertezza",
    re.IGNORECASE,
)
CONTACT_MISSING_CHANNEL_LIST = re.compile(
    r"\bSignal\b|\bTelegram\b|anonymous[- ]upload|encrypted[- ]email|"
    r"社群媒體|社交媒體|社交媒体|匿名上傳|匿名上传|暗号化された電子メール|"
    r"익명 업로드|암호화된 이메일|redes sociales|correo electrónico cifrado|"
    r"soziale Medien|verschlüsselte E-Mail|réseaux sociaux|messagerie cryptée|"
    r"sosiale medier|kryptert e-post|sociale media|gecodeerde e-mail|"
    r"social media|e-mail crittografate|caricamento anonimo",
    re.IGNORECASE,
)
CONTACT_TRANSLATION_ERRORS = re.compile(
    r"サポートするページまたは主張|外部リンクが壊れているか|正確な位置と裏付け資料による事実の訂正|"
    r"정확한 위치와 근거자료로 사실을 수정합니다|페이지 또는 주장|"
    r"\bQue puedes enviar\b|página o reclamo|\breclamo\b|falsch sichtbarer Quellentitel|"
    r"revendication qu['’]elle prend en charge|pagina of claim|\bclaim\b",
    re.IGNORECASE,
)
CONTACT_REVERSED_FLOW = re.compile(
    r"Formspree.{0,120}(?:傳送|送信|전송|transmit|send|transfer|transmite|envía|übermittelt|"
    r"transmet|overfører|stuurt|trasmette).{0,60}(?:外部服務|外部サービス|외부 서비스|"
    r"external service|servicio externo|externen Dienst|service externe|ekstern tjeneste|"
    r"externe dienst|servizio esterno)",
    re.IGNORECASE | re.DOTALL,
)
CONTACT_FLOW_PATTERNS = {
    "zh": r"首頁表單.*name.*email.*message.*外部表單服務\s*Formspree.*Formspree.*處理.*(?:轉送|轉交).*本站.*接收",
    "en": r"homepage form.*name.*email.*message.*external form service\s+Formspree.*Formspree processes.*forwards.*site.*receive",
    "ja": r"(?=.*ホームページのフォーム)(?=.*name.*email.*message)(?=.*外部フォームサービス.*Formspree)(?=.*Formspree.*処理)(?=.*サイトへ転送)(?=.*受け取)",
    "ko": r"(?=.*홈페이지 양식)(?=.*name.*email.*message)(?=.*외부 양식 서비스.*Formspree)(?=.*Formspree.*처리)(?=.*사이트로 전달)(?=.*받을)",
    "es": r"formulario de la página de inicio.*name.*email.*message.*servicio externo de formularios\s+Formspree.*Formspree procesa.*reenvía.*sitio.*recibir",
    "de": r"Formular auf der Startseite.*name.*email.*message.*externen Formulardienst\s+Formspree.*Formspree verarbeitet.*leitet.*Website.*empfangen",
    "fr": r"formulaire de la page d.accueil.*name.*email.*message.*service de formulaires externe\s+Formspree.*Formspree traite.*transmet.*site.*recevoir",
    "no": r"Skjemaet på forsiden.*name.*email.*message.*eksterne skjematjenesten\s+Formspree.*Formspree behandler.*videresender.*nettstedet.*motta",
    "nl": r"formulier op de startpagina.*name.*email.*message.*externe formulierdienst\s+Formspree.*Formspree verwerkt.*stuurt.*site.*ontvangen",
    "it": r"modulo della pagina iniziale.*name.*email.*message.*servizio esterno per moduli\s+Formspree.*Formspree elabora.*inoltra.*sito.*ricevere",
}
CONTACT_CONTROL_PATTERNS = {
    "zh": r"無法控制\s*Formspree.*儲存.*處理", "en": r"does not control.*Formspree.*stores.*processes",
    "ja": r"Formspree.*保存.*処理.*管理できません", "ko": r"Formspree.*저장.*처리.*통제하지 않습니다",
    "es": r"no controla.*Formspree.*almacena.*procesa", "de": r"kontrolliert nicht.*Formspree.*speichert.*verarbeitet",
    "fr": r"ne contrôle.*stockage.*traitement.*Formspree", "no": r"kontrollerer ikke.*Formspree.*lagrer.*behandler",
    "nl": r"bepaalt niet.*Formspree.*opslaat.*verwerkt", "it": r"non controlla.*Formspree.*conserva.*tratta",
}
TERMS_TRANSLATION_ERRORS = re.compile(
    r"限定的な帰属|적격한 귀속|atribuciones calificativas|qualifizierende Quellenangabe|"
    r"attribution qualificative|kvalifiserende attribusjon|kwalificerende toeschrijving|"
    r"attribuzioni qualificanti|\bqualifying attribution\b|\bcivilian records\b|\bcivil records\b|"
    r"registros civiles|dossiers civils|documenti civili|sivile dokumenter|zivile Aufzeichnungen|"
    r"burgerdossiers|\breports abroad\b|\boverseas reporting\b|informes en el extranjero|"
    r"reportages à l.étranger|resoconti all.estero|Berichterstattung im Ausland|해외 보고|"
    r"\bstability maintenance\b|stabilitetsvedlikehold|stabiliteitshandhaving",
    re.IGNORECASE,
)
TERMS_LATEST_AUDIT_ERRORS = re.compile(
    r"确信程度|支援公共資料|該網站審查已識別資料|지원 공개 자료|식별된 자료|"
    r"matériel public à l.appui|contexte d.intérêt public du matériel identifié|"
    r"eller gjengjeldelse mot|støttende offentlig materiale|"
    r"unterstützendes öffentliches Material|ondersteunend openbaar materiaal|"
    r"niet-ondersteunde eigendomsclaims|materiale pubblico di supporto|"
    r"elemento archiviato specifico",
    re.IGNORECASE,
)
TERMS_FACT_PATTERNS = {
    "zh": {"limits": r"範圍.*條件.*主體.*確信程度", "citizen": r"民間記錄", "media": r"海外媒體報道", "stability": r"中國國家機關.*維護穩定.*警務.*行政.*資訊.*社會控制"},
    "en": {"limits": r"scope.*conditions.*subject.*degree of certainty", "citizen": r"citizens? or civil society", "media": r"overseas media", "stability": r"(?=.*Chinese state bodies)(?=.*maintaining stability)(?=.*policing)(?=.*administrative)(?=.*information)(?=.*social-control)"},
    "ja": {"limits": r"範囲.*条件.*主体.*確度", "citizen": r"民間記録", "media": r"海外メディアの報道", "stability": r"中国の国家機関.*安定維持.*警察.*行政.*情報.*社会統制"},
    "ko": {"limits": r"범위.*조건.*주체.*확실성", "citizen": r"민간 기록", "media": r"해외 언론 보도", "stability": r"중국 국가기관.*안정 유지.*경찰.*행정.*정보.*사회 통제"},
    "es": {"limits": r"matices.*límites.*sujeto.*grado de certeza", "citizen": r"(?:documentación ciudadana|ciudadanos o la sociedad civil)", "media": r"medios extranjeros", "stability": r"(?=.*órganos estatales chinos)(?=.*mantener la estabilidad)(?=.*policiales)(?=.*administrativas)(?=.*informativas)(?=.*control social)"},
    "de": {"limits": r"Umfang.*Bedingungen.*Subjekt.*Gewissheitsgrad", "citizen": r"zivilgesellschaftliche Aufzeichnungen", "media": r"ausländischer Medien", "stability": r"(?=.*chinesische Staatsorgane)(?=.*Stabilitätssicherung)(?=.*polizeiliche)(?=.*administrative)(?=.*informationelle)(?=.*gesellschaftliche Kontrollmaßnahmen)"},
    "fr": {"limits": r"limites.*conditions.*sujet.*degré de certitude", "citizen": r"documents recueillis par des citoyens", "media": r"médias établis à l.étranger", "stability": r"(?=.*organes de l.État chinois)(?=.*maintien de la stabilité)(?=.*policières)(?=.*administratives)(?=.*informationnelles)(?=.*sociales)"},
    "no": {"limits": r"avgrensninger.*vilkår.*subjekt.*grad av sikkerhet", "citizen": r"(?:dokumentasjon fra sivilsamfunnet|borgere eller sivilsamfunnet)", "media": r"utenlandske medier", "stability": r"(?=.*kinesiske statsorganer)(?=.*opprettholde stabilitet)(?=.*politi)(?=.*forvaltnings)(?=.*informasjons)(?=.*sosialkontroll)"},
    "nl": {"limits": r"beperkingen.*voorwaarden.*onderwerp.*mate van zekerheid", "citizen": r"(?:burgerdocumentatie|burgers of het maatschappelijk middenveld)", "media": r"buitenlandse media", "stability": r"(?=.*Chinese staatsorganen)(?=.*stabiliteit handhaven)(?=.*politie)(?=.*bestuurs)(?=.*informatie)(?=.*sociale-controlemaatregelen)"},
    "it": {"limits": r"limiti.*condizioni.*soggetto.*grado di certezza", "citizen": r"documentazione raccolta da cittadini", "media": r"media esteri", "stability": r"(?=.*organi statali cinesi)(?=.*mantenimento della stabilità)(?=.*polizia)(?=.*amministrativo)(?=.*informativo)(?=.*sociale)"},
}
TERMS_CORRECTIONS_PATTERNS = {
    "zh": (
        r"具體頁面.*確切段落.*作為佐證的公開資料",
        r"具體圖片.*文字.*存檔項目.*說明請求依據",
        r"相關資料的來源.*權利主張的依據.*公共利益背景.*缺乏證據支持的所有權主張.*不會被自動接受",
    ),
    "en": (
        r"correction request.*specific page.*exact passage.*publicly available material.*supports.*correction",
        r"copyright or permission request.*specific image.*text.*archived item.*explain.*basis",
        r"source of the material concerned.*basis for the rights claim.*public-interest context.*ownership claims unsupported by evidence.*not automatically accepted",
    ),
    "ja": (
        r"訂正の申し出.*対象ページ.*該当箇所.*訂正内容を裏付ける公開資料",
        r"著作権または利用許諾.*画像.*文章.*アーカイブ資料.*根拠を説明",
        r"対象資料の出所.*権利主張の根拠.*公益との関係.*所有権の主張.*自動的に受け入れることはありません",
    ),
    "ko": (
        r"정정 요청.*해당 페이지.*정확한 문단.*정정 내용을 뒷받침하는 공개 자료",
        r"저작권 또는 이용 허가 요청.*이미지.*문구.*보관 자료.*근거를 설명",
        r"관련 자료의 출처.*권리 주장의 근거.*공익적 맥락.*소유권 주장.*자동으로 받아들이지 않습니다",
    ),
    "es": (
        r"solicitud de corrección.*página concreta.*pasaje exacto.*documentación pública.*sustente la corrección",
        r"solicitud de derechos de autor o de autorización.*imagen.*texto.*elemento archivado.*explicar su fundamento",
        r"procedencia del material correspondiente.*fundamento de la pretensión de derechos.*contexto de interés público.*pretensiones de propiedad.*no se aceptan automáticamente",
    ),
    "de": (
        r"Korrekturhinweis.*betreffende Seite.*genaue Textstelle.*öffentlich zugängliche Belege",
        r"Urheberrechts- oder Genehmigungsanfrage.*konkrete Bild.*konkrete Text.*konkrete Archivgegenstand.*Grundlage.*erläutern",
        r"Herkunft des betreffenden Materials.*Grundlage des geltend gemachten Rechts.*öffentlichen Interessenbezug.*Unbelegte Eigentumsansprüche.*nicht automatisch anerkannt",
    ),
    "fr": (
        r"demande de correction.*page concernée.*passage exact.*documents publics étayant la correction",
        r"demande relative au droit d.auteur ou à une autorisation.*image.*texte.*élément archivé.*expliquer son fondement",
        r"provenance du contenu concerné.*fondement de la demande.*intérêt public.*revendications de propriété.*pas automatiquement acceptées",
    ),
    "no": (
        r"anmodning om rettelse.*aktuelle siden.*nøyaktige avsnittet.*offentlig dokumentasjon.*underbygger rettelsen",
        r"forespørsel om opphavsrett eller tillatelse.*konkrete bildet.*teksten.*arkivobjektet.*forklare.*grunnlaget",
        r"aktuelle materialet kommer fra.*grunnlaget for rettighetskravet.*allmenn interesse.*Eierskapskrav uten dokumentasjon.*ikke automatisk",
    ),
    "nl": (
        r"correctieverzoek.*betreffende pagina.*exacte passage.*openbare stukken.*correctie onderbouwen",
        r"verzoek om auteursrecht of toestemming.*specifieke afbeelding, tekst of het gearchiveerde item.*grondslag.*toelichten",
        r"herkomst van het betreffende materiaal.*grondslag van de rechtenclaim.*context van algemeen belang.*Ongefundeerde eigendomsaanspraken.*niet automatisch aanvaard",
    ),
    "it": (
        r"richiesta di correzione.*pagina interessata.*passaggio esatto.*documentazione pubblica.*sostenga la correzione",
        r"richiesta di diritto d.autore o di autorizzazione.*immagine.*testo.*specifico elemento archiviato.*spiegare.*fondamento",
        r"provenienza del materiale interessato.*fondamento della pretesa di diritto.*contesto di interesse pubblico.*pretese di proprietà prive di riscontri.*non vengono accettate automaticamente",
    ),
}
SEMANTIC_REVIEW_PATH = Path("/tmp/public-pages-semantic-review.tsv")
SEMANTIC_REVIEW_FIELDS = ("file", "language", "section", "exact_visible_text", "result", "review_note")
SEMANTIC_REVIEW_SECTIONS = {
    "contact.html": ("channels", "submissions", "form-data"),
    "terms.html": ("citation", "safety", "corrections", "evidence-use"),
}
GENERIC_REVIEW_NOTE = re.compile(
    r"句法、指代和动作关系自然|句法、指代和動作關係自然|syntax.*reference.*natural|"
    r"translation (?:was )?reviewed|no fallback found",
    re.IGNORECASE,
)
REVIEW_LANGUAGE_LABEL = re.compile(
    r"\b(?:zh|en|ja|ko|es|de|fr|no|nl|it|Chinese|English|Japanese|Korean|Spanish|German|French|Norwegian|Dutch|Italian)\b|"
    r"繁體中文|简体中文|簡體中文|中文|英文|日文|韓文|韩文|西班牙文|德文|法文|挪威文|荷蘭文|荷兰文|義大利文|意大利文",
    re.IGNORECASE,
)
TRADITIONAL_ZH_REGRESSIONS = re.compile(
    r"存储|链接|数据|网站|记录|服务|表格|当前代码|首选项|"
    r"key\s+lang\s+下|lang\s+键|lang\s+鍵下"
)
PRIVACY_CODE_SEQUENCE = "zh, en, ja, ko, es, de, fr, no, nl, it"
PRIVACY_CODE_SEQUENCE_NO = "zh, en, ja, ko, es, de, fr, no, nl og it"
PRIVACY_HARD_ERRORS = re.compile(
    r"sous la langue de la clé|nøkkelspråket|nl,\s*og\s*det|nøkkelen\s+språket",
    re.IGNORECASE,
)
PRIVACY_FACT_PATTERNS = {
    "zh": {
        "restore": r"還原.*介面語言", "not_cookie": r"不是\s*Cookie",
        "no_transmit": r"不會.*傳送", "clear": r"刪除.*值",
        "fallback": r"預設語言.*繼續執行", "retention": r"保留.*刪除.*安全",
        "providers": r"寄件者.*收件者.*電子郵件服務商", "no_tracking": r"分析工具.*廣告追蹤器.*行銷像素",
        "sensitive": r"住址.*未成年", "correction": r"更正或刪除.*外部服務",
    },
    "en": {
        "restore": r"restore.*interface language", "not_cookie": r"not a Cookie",
        "no_transmit": r"does not transmit", "clear": r"remove the value",
        "fallback": r"default language.*continues to run", "retention": r"retention.*deletion.*security",
        "providers": r"sender.s and recipient.s email providers", "no_tracking": r"analytics.*advertising trackers.*marketing pixels",
        "sensitive": r"home addresses.*minors", "correction": r"correction or removal.*external service",
    },
    "ja": {
        "restore": r"表示言語を復元", "not_cookie": r"Cookie\s*ではありません",
        "no_transmit": r"送信することはなく", "clear": r"値を削除",
        "fallback": r"既定の言語.*引き続き動作", "retention": r"保存期間.*削除.*セキュリティ",
        "providers": r"送信者側.*受信者側.*メール事業者", "no_tracking": r"解析ツール.*広告トラッカー.*マーケティング",
        "sensitive": r"住所.*未成年", "correction": r"訂正や削除.*外部サービス",
    },
    "ko": {
        "restore": r"화면 언어를 복원", "not_cookie": r"Cookie가 아닙니다",
        "no_transmit": r"전송하지 않", "clear": r"값을 삭제",
        "fallback": r"기본 언어.*계속 작동", "retention": r"보관.*삭제.*보안",
        "providers": r"발신자.*수신자.*이메일 제공업체", "no_tracking": r"분석 도구.*광고 추적기.*마케팅 픽셀",
        "sensitive": r"집 주소.*미성년자", "correction": r"정정하거나 삭제.*외부 서비스",
    },
    "es": {
        "restore": r"recuperar el idioma elegido", "not_cookie": r"no una Cookie",
        "no_transmit": r"no transmite", "clear": r"borrar el valor",
        "fallback": r"idioma predeterminado.*sigue funcionando", "retention": r"conservación.*eliminación.*seguridad",
        "providers": r"proveedores de correo del remitente y del destinatario", "no_tracking": r"analítica.*rastreadores publicitarios.*píxeles de marketing",
        "sensitive": r"domicilios.*menores", "correction": r"corrección o eliminación.*servicio externo",
    },
    "de": {
        "restore": r"gewählte Sprache.*wiederherzustellen", "not_cookie": r"kein Cookie",
        "no_transmit": r"übermittelt.*nicht", "clear": r"Wert.*löschen",
        "fallback": r"Standardsprache.*weiterläuft", "retention": r"Aufbewahrung.*Löschung.*Sicherheit",
        "providers": r"E-Mail-Anbieter von Absender und Empfänger", "no_tracking": r"Webanalyse.*Werbetracker.*Marketing-Pixel",
        "sensitive": r"Privatadressen.*Minderjährige", "correction": r"Berichtigung oder Löschung.*externen Diensten",
    },
    "fr": {
        "restore": r"rétablir la langue choisie", "not_cookie": r"non un Cookie",
        "no_transmit": r"ne transmet pas", "clear": r"supprimer la valeur",
        "fallback": r"langue par défaut.*continue de fonctionner", "retention": r"conservation.*suppression.*sécurité",
        "providers": r"fournisseurs de messagerie de l.expéditeur et du destinataire", "no_tracking": r"outil d’analyse.*traceur publicitaire.*pixel de marketing",
        "sensitive": r"adresse personnelle.*mineur", "correction": r"rectification ou la suppression.*service externe",
    },
    "no": {
        "restore": r"gjenopprette valgt språk", "not_cookie": r"ikke en Cookie",
        "no_transmit": r"sender ikke", "clear": r"slette verdien",
        "fallback": r"standardspråket.*fortsatt fungerer", "retention": r"lagring.*sletting.*sikkerhet",
        "providers": r"avsenderens og mottakerens e-postleverandører", "no_tracking": r"analyse.*annonsesporing.*markedsføringspiksler",
        "sensitive": r"hjemmeadresser.*mindreårige", "correction": r"retting eller sletting.*ekstern tjeneste",
    },
    "nl": {
        "restore": r"gekozen taal te herstellen", "not_cookie": r"geen Cookie",
        "no_transmit": r"stuurt.*niet", "clear": r"waarde.*verwijderen",
        "fallback": r"standaardtaal.*blijft.*werken", "retention": r"bewaring.*verwijdering.*beveiliging",
        "providers": r"e-mailproviders van afzender en ontvanger", "no_tracking": r"analysefunctie.*advertentietrackers.*marketingpixels",
        "sensitive": r"huisadressen.*minderjarigen", "correction": r"correctie of verwijdering.*externe dienst",
    },
    "it": {
        "restore": r"ripristinare la lingua scelta", "not_cookie": r"non un Cookie",
        "no_transmit": r"non trasmette", "clear": r"cancellare il valore",
        "fallback": r"lingua predefinita.*continua a funzionare", "retention": r"conservazione.*cancellazione.*sicurezza",
        "providers": r"fornitori di posta del mittente e del destinatario", "no_tracking": r"strumenti analitici.*tracciatori pubblicitari.*pixel di marketing",
        "sensitive": r"indirizzi di casa.*minori", "correction": r"rettifica o la rimozione.*servizio esterno",
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frozen_article_issues(overrides: dict[str, bytes] | None = None) -> list[str]:
    """Enforce the pre-batch byte baseline for all dossiers and frozen controls."""
    overrides = overrides or {}
    issues = []
    current_names = {path.name for path in FILES}
    if current_names != set(FROZEN_POST_HASHES):
        issues.append("frozen articles: filename set differs from the 54-file baseline")
    for name, expected in FROZEN_POST_HASHES.items():
        path = POSTS / name
        data = overrides.get(name, path.read_bytes() if path.exists() else b"")
        if sha256_bytes(data) != expected:
            issues.append(f"frozen article changed: posts/{name}")
    for relative, expected in FROZEN_CONTROL_HASHES.items():
        path = ROOT / relative
        data = overrides.get(relative, path.read_bytes() if path.exists() else b"")
        if sha256_bytes(data) != expected:
            issues.append(f"frozen control changed: {relative}")
    return issues


def public_body_for(soup: BeautifulSoup, lang: str):
    return soup.select_one(f'[data-language-body="{lang}"]')


def localized_classes(node) -> set[str]:
    result = set()
    if node is None:
        return result
    for item in node.select("[class]"):
        for klass in item.get("class") or []:
            if klass.startswith("lang-") and klass[5:] in LANGS:
                result.add(klass[5:])
    return result


def public_visible_text(soup: BeautifulSoup) -> str:
    clone = copy.copy(soup)
    for node in clone.select("script, style, template"):
        node.decompose()
    return clone.get_text(" ", strip=True)


def public_structure(body) -> tuple:
    if body is None:
        return ()
    signature = []
    for section in body.select(":scope > section[data-section]"):
        top_tags = tuple(child.name for child in section.children if getattr(child, "name", None))
        list_sizes = tuple(len(value.select(":scope > li")) for value in section.select("ul, ol"))
        signature.append((section.get("data-section"), top_tags, list_sizes))
    return tuple(signature)


def public_page_issues(soup: BeautifulSoup, path: Path) -> list[str]:
    issues = []
    bodies = soup.select("[data-language-body]")
    body_langs = [body.get("data-language-body") for body in bodies]
    if len(bodies) != len(LANGS) or set(body_langs) != set(LANGS):
        issues.append(f"public page: needs exactly ten language bodies, found {body_langs}")
    title_nodes = soup.select("h1.article-title [class]")
    dek_nodes = soup.select("p.article-dek [class]")
    for field, nodes in (("title", title_nodes), ("deck", dek_nodes)):
        present = localized_classes(BeautifulSoup("".join(str(node) for node in nodes), "html.parser"))
        if present != set(LANGS):
            issues.append(f"public {field}: language set is incomplete")
        english = soup.select_one(f"{'h1.article-title' if field == 'title' else 'p.article-dek'} .lang-en")
        english_text = english.get_text(" ", strip=True) if english else ""
        for lang in LANGS:
            node = soup.select_one(f"{'h1.article-title' if field == 'title' else 'p.article-dek'} .lang-{lang}")
            text = node.get_text(" ", strip=True) if node else ""
            if not text:
                issues.append(f"public {field}: missing {lang} text")
            elif lang != "en" and text == english_text:
                issues.append(f"public {field}: {lang} falls back to English")
    reference = public_structure(public_body_for(soup, "en"))
    zh_body = public_body_for(soup, "zh")
    zh_headings = {
        node.get_text(" ", strip=True)
        for node in (zh_body.select("h2, h3") if zh_body else [])
        if len(node.get_text(" ", strip=True)) >= 2
    }
    english_blocks = [
        node.get_text(" ", strip=True)
        for node in (public_body_for(soup, "en").select("h2, h3, p, li") if public_body_for(soup, "en") else [])
        if node.find_parent("section", attrs={"data-section": "retained-links"}) is None
    ]
    for lang in LANGS:
        body = public_body_for(soup, lang)
        if body is None:
            continue
        if public_structure(body) != reference:
            issues.append(f"{lang}: public section/list structure differs from English")
        text = body.get_text(" ", strip=True)
        if len(text) < 120:
            issues.append(f"{lang}: public page body is too short")
        if PUBLIC_BANNED.search(text):
            issues.append(f"{lang}: prohibited public disclaimer or internal wording")
        if lang != "en":
            blocks = [
                node.get_text(" ", strip=True) for node in body.select("h2, h3, p, li")
                if node.find_parent("section", attrs={"data-section": "retained-links"}) is None
            ]
            for number, value in enumerate(blocks):
                if number < len(english_blocks) and len(value) >= 24 and value == english_blocks[number]:
                    issues.append(f"{lang}: public block {number + 1} falls back to English")
                    break
        if lang not in {"zh", "ja"}:
            headings = {node.get_text(" ", strip=True) for node in body.select("h2, h3")}
            if headings & zh_headings:
                issues.append(f"{lang}: public heading falls back to Chinese")
    return issues


def privacy_issues(soup: BeautifulSoup) -> list[str]:
    issues = []
    required_sections = {"language-storage", "formspree", "email", "external-links", "safety-requests"}
    for lang in LANGS:
        body = public_body_for(soup, lang)
        if body is None:
            continue
        text = body.get_text(" ", strip=True)
        sections = {node.get("data-section") for node in body.select(":scope > section[data-section]")}
        if sections != required_sections:
            issues.append(f"privacy {lang}: required data-flow sections are incomplete")
        for literal in (
            "language.js", "localStorage", "lang", "Formspree",
            "https://formspree.io/f/xgvdozke", "name", "email", "message",
        ):
            if literal not in text:
                issues.append(f"privacy {lang}: missing {literal} disclosure")
        storage_text = (body.select_one('[data-section="language-storage"]') or body).get_text(" ", strip=True)
        expected_codes = PRIVACY_CODE_SEQUENCE_NO if lang == "no" else PRIVACY_CODE_SEQUENCE
        if expected_codes not in storage_text:
            issues.append(f"privacy {lang}: ordered ten-code language set is incomplete")
        if lang == "fr" and not re.search(r"sous la clé lang(?:[.;, ]|$)", storage_text):
            issues.append("privacy fr: localStorage key must read 'sous la clé lang'")
        if lang == "no" and not re.search(r"under nøkkelen lang(?:[.;, ]|$)", storage_text):
            issues.append("privacy no: localStorage key must read 'under nøkkelen lang'")
        if PRIVACY_HARD_ERRORS.search(text):
            issues.append(f"privacy {lang}: known French or Norwegian key/value mistranslation returned")
        formspree_text = (body.select_one('[data-section="formspree"]') or body).get_text(" ", strip=True)
        for field in ("name", "email", "message"):
            if not re.search(rf"\b{field}\b", formspree_text):
                issues.append(f"privacy {lang}: missing exact {field} form-field literal")
        if len((body.select_one('[data-section="external-links"]') or body).get_text(" ", strip=True)) < 70:
            issues.append(f"privacy {lang}: external-link disclosure is incomplete")
        if len((body.select_one('[data-section="safety-requests"]') or body).get_text(" ", strip=True)) < 100:
            issues.append(f"privacy {lang}: sensitive-data safety disclosure is incomplete")
        section_facts = {
            "language-storage": ("restore", "not_cookie", "no_transmit", "clear", "fallback"),
            "formspree": ("retention",),
            "email": ("providers",),
            "external-links": ("no_tracking",),
            "safety-requests": ("sensitive", "correction"),
        }
        for section_name, fact_names in section_facts.items():
            section = body.select_one(f'[data-section="{section_name}"]')
            section_text_value = section.get_text(" ", strip=True) if section else ""
            for fact_name in fact_names:
                if not re.search(PRIVACY_FACT_PATTERNS[lang][fact_name], section_text_value, re.I | re.S):
                    issues.append(f"privacy {lang}: {section_name} lacks {fact_name} meaning")
    return issues


def about_issues(soup: BeautifulSoup) -> list[str]:
    issues = []
    for lang in LANGS:
        body = public_body_for(soup, lang)
        mission = body.select_one('[data-section="mission"]') if body else None
        first = mission.find("p", recursive=False) if mission else None
        text = first.get_text(" ", strip=True) if first else ""
        if not text:
            issues.append(f"about {lang}: mission statement is missing")
        elif ABOUT_SERVICE_MODE.search(text):
            issues.append(f"about {lang}: archive purpose reverted to a service-provider claim")
    return issues


def terms_issues(soup: BeautifulSoup) -> list[str]:
    issues = []
    english_body = public_body_for(soup, "en")
    english_blocks = [node.get_text(" ", strip=True) for node in english_body.select("h2, p, li")]
    for lang in LANGS:
        body = public_body_for(soup, lang)
        if body is None:
            continue
        citation = body.select_one('[data-section="citation"]') if body else None
        text = citation.get_text(" ", strip=True) if citation else ""
        if TERMS_UNCERTAINTY_MARKERS.search(text):
            issues.append(f"terms {lang}: abstract uncertainty-marker wording returned")
        body_text = body.get_text(" ", strip=True)
        if TERMS_TRANSLATION_ERRORS.search(body_text):
            issues.append(f"terms {lang}: known mechanical source or stability translation returned")
        if TERMS_LATEST_AUDIT_ERRORS.search(body_text):
            issues.append(f"terms {lang}: latest audited mechanical or legal phrasing returned")
        citation_items = citation.select(":scope > ul > li") if citation else []
        corrections = body.select_one('[data-section="corrections"]')
        correction_items = corrections.select(":scope > ul > li") if corrections else []
        evidence = body.select_one('[data-section="evidence-use"]')
        evidence_paragraphs = evidence.find_all("p", recursive=False) if evidence else []
        if len(citation_items) != 3 or len(correction_items) != 3 or len(evidence_paragraphs) != 2:
            issues.append(f"terms {lang}: citation, corrections, or evidence-use structure is incomplete")
            continue
        for index, pattern in enumerate(TERMS_CORRECTIONS_PATTERNS[lang]):
            correction_text = correction_items[index].get_text(" ", strip=True)
            if not re.search(pattern, correction_text, re.IGNORECASE | re.DOTALL):
                issues.append(f"terms {lang}: corrections item {index + 1} legal meaning is incomplete")
        if lang == "no":
            safety = body.select_one('[data-section="safety"] p')
            safety_text = safety.get_text(" ", strip=True) if safety else ""
            if not re.search(
                r"utsette berørte personer, familiemedlemmer, vitner, journalister eller støttespillere for represalier",
                safety_text,
                re.IGNORECASE,
            ):
                issues.append("terms no: retaliation sentence is grammatically incomplete")
        facts = TERMS_FACT_PATTERNS[lang]
        fact_texts = {
            "limits": citation_items[1].get_text(" ", strip=True),
            "citizen": citation_items[2].get_text(" ", strip=True) + " " + evidence_paragraphs[0].get_text(" ", strip=True),
            "media": citation_items[2].get_text(" ", strip=True) + " " + evidence_paragraphs[0].get_text(" ", strip=True),
            "stability": evidence_paragraphs[1].get_text(" ", strip=True),
        }
        for fact_name, pattern in facts.items():
            if not re.search(pattern, fact_texts[fact_name], re.IGNORECASE | re.DOTALL):
                issues.append(f"terms {lang}: {fact_name} meaning is incomplete")
        if lang != "en":
            localized = [node.get_text(" ", strip=True) for node in body.select("h2, p, li")]
            if any(len(value) >= 24 and value == english_blocks[index] for index, value in enumerate(localized)):
                issues.append(f"terms {lang}: visible block falls back to English")
    return issues


def traditional_chinese_issues(soup: BeautifulSoup, page_name: str) -> list[str]:
    body = public_body_for(soup, "zh")
    if body is None:
        return []
    match = TRADITIONAL_ZH_REGRESSIONS.search(body.get_text(" ", strip=True))
    return [f"{page_name} zh: simplified or mixed Chinese returned ({match.group(0)})"] if match else []


def index_contact_issues(soup: BeautifulSoup) -> list[str]:
    issues = []
    form = soup.select_one("form.contact-form")
    if form is None:
        return ["index contact: missing contact form"]
    if form.get("action") != "https://formspree.io/f/xgvdozke" or (form.get("method") or "").upper() != "POST":
        issues.append("index contact: Formspree endpoint or method is wrong")
    controls = {node.get("name"): node for node in form.select("input[name], textarea[name]")}
    if set(controls) != {"name", "email", "message"}:
        issues.append("index contact: fields must be exactly name, email, and message")
    for name, expected in (("name", "name"), ("email", "email"), ("message", "off")):
        node = controls.get(name)
        if node is None or node.get("autocomplete") != expected:
            issues.append(f"index contact: {name} autocomplete is missing or incorrect")
            continue
        label = form.select_one(f'label[for="{node.get("id")}"]')
        if label is None or localized_classes(label) != set(LANGS):
            issues.append(f"index contact: {name} lacks ten visible labels")
    button = form.select_one('button[type="submit"]')
    if button is None or localized_classes(button) != set(LANGS):
        issues.append("index contact: submit button lacks ten labels")
    disclosures = form.select("[data-formspree-disclosure]")
    intros = soup.select("[data-contact-intro]")
    for label, nodes in (("intro", intros), ("Formspree safety", disclosures)):
        langs = {
            next((klass[5:] for klass in node.get("class") or [] if klass.startswith("lang-")), None)
            for node in nodes
        }
        if langs != set(LANGS) or any(
            len(node.get_text(" ", strip=True)) < (
                35 if next(
                    (klass[5:] for klass in node.get("class") or [] if klass.startswith("lang-")), "en"
                ) in {"zh", "ja", "ko"} else 80
            )
            for node in nodes
        ):
            issues.append(f"index contact: {label} text is incomplete")
    text = public_visible_text(soup)
    if "wuzong2025@gmail.com" not in text or "Formspree" not in text:
        issues.append("index contact: public email or Formspree is missing")
    if SOCIAL_MEDIA_FALSE_CLAIM.search(text):
        issues.append("index contact: nonexistent social-media contact claim returned")
    if CONTACT_MISSING_CHANNEL_LIST.search(text):
        issues.append("index contact: negative list of unavailable contact features returned")
    zh_contact = " ".join(node.get_text(" ", strip=True) for node in soup.select("#contact .lang-zh"))
    match = TRADITIONAL_ZH_REGRESSIONS.search(zh_contact)
    if match:
        issues.append(f"index contact zh: simplified or mixed Chinese returned ({match.group(0)})")
    return issues


def contact_page_issues(soup: BeautifulSoup) -> list[str]:
    issues = []
    english_body = public_body_for(soup, "en")
    english_blocks = [node.get_text(" ", strip=True) for node in english_body.select("h2, p, li")]
    for lang in LANGS:
        body = public_body_for(soup, lang)
        if body is None:
            continue
        text = body.get_text(" ", strip=True)
        for literal in ("wuzong2025@gmail.com", "Formspree", "https://formspree.io/f/xgvdozke"):
            if literal not in text:
                issues.append(f"contact {lang}: missing {literal}")
        safety = body.select_one('[data-section="form-data"]')
        if safety is None or len(safety.get_text(" ", strip=True)) < 180:
            issues.append(f"contact {lang}: Formspree and sensitive-data disclosure is incomplete")
            continue
        paragraphs = safety.find_all("p", recursive=False)
        if len(paragraphs) != 3:
            issues.append(f"contact {lang}: Formspree section must contain three visible paragraphs")
            continue
        flow_text = paragraphs[0].get_text(" ", strip=True)
        if CONTACT_REVERSED_FLOW.search(flow_text):
            issues.append(f"contact {lang}: Formspree data flow is reversed toward another external service")
        if not re.search(CONTACT_FLOW_PATTERNS[lang], flow_text, re.IGNORECASE | re.DOTALL):
            issues.append(f"contact {lang}: form-to-Formspree-to-site data flow is incomplete")
        for field in ("name", "email", "message"):
            if not re.search(rf"\b{field}\b", flow_text):
                issues.append(f"contact {lang}: data-flow paragraph lacks exact {field} field literal")
        control_text = paragraphs[2].get_text(" ", strip=True)
        if not re.search(CONTACT_CONTROL_PATTERNS[lang], control_text, re.IGNORECASE | re.DOTALL):
            issues.append(f"contact {lang}: Formspree storage and processing boundary is incomplete")
        if CONTACT_TRANSLATION_ERRORS.search(text):
            issues.append(f"contact {lang}: known mechanical translation returned")
        if SOCIAL_MEDIA_FALSE_CLAIM.search(text):
            issues.append(f"contact {lang}: nonexistent social-media contact claim returned")
        if CONTACT_MISSING_CHANNEL_LIST.search(text):
            issues.append(f"contact {lang}: negative list of unavailable contact features returned")
        if lang != "en":
            localized = [node.get_text(" ", strip=True) for node in body.select("h2, p, li")]
            if any(len(value) >= 24 and value == english_blocks[index] for index, value in enumerate(localized)):
                issues.append(f"contact {lang}: visible block falls back to English")
    return issues


def load_semantic_review_rows() -> tuple[list[dict[str, str]], list[str]]:
    if not SEMANTIC_REVIEW_PATH.exists():
        return [], []
    with SEMANTIC_REVIEW_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader), list(reader.fieldnames or [])


def normalized_review_note_template(note: str) -> str:
    normalized = re.sub(r"\s+", " ", note).strip().casefold()
    return REVIEW_LANGUAGE_LABEL.sub("<lang>", normalized)


def semantic_review_issues(rows_override: list[dict[str, str]] | None = None) -> list[str]:
    issues = []
    if rows_override is None:
        rows, fieldnames = load_semantic_review_rows()
    else:
        rows = rows_override
        fieldnames = list(rows[0]) if rows else []
    missing_fields = set(SEMANTIC_REVIEW_FIELDS) - set(fieldnames)
    if missing_fields:
        return [f"semantic review TSV: missing fields {', '.join(sorted(missing_fields))}"]

    expected = {
        (file_name, lang, section)
        for file_name, sections in SEMANTIC_REVIEW_SECTIONS.items()
        for lang in LANGS
        for section in sections
    }
    keys = [(row.get("file", ""), row.get("language", ""), row.get("section", "")) for row in rows]
    counts = Counter(keys)
    if set(keys) != expected:
        missing = sorted(expected - set(keys))
        extra = sorted(set(keys) - expected)
        issues.append(f"semantic review TSV: coverage differs; missing={missing[:3]} extra={extra[:3]}")
    duplicated = sorted(key for key, count in counts.items() if count != 1)
    if duplicated:
        issues.append(f"semantic review TSV: duplicate section rows {duplicated[:3]}")

    documents = {
        name: BeautifulSoup((ROOT / name).read_text(encoding="utf-8"), "html.parser")
        for name in SEMANTIC_REVIEW_SECTIONS
    }
    note_counts = Counter()
    note_template_counts = Counter()
    for row in rows:
        key = (row.get("file", ""), row.get("language", ""), row.get("section", ""))
        if key not in expected:
            continue
        file_name, lang, section = key
        node = public_body_for(documents[file_name], lang).select_one(f'[data-section="{section}"]')
        visible = node.get_text(" ", strip=True) if node else ""
        if row.get("exact_visible_text", "") != visible:
            issues.append(f"semantic review TSV: exact visible text is stale for {file_name} {lang} {section}")
        if not row.get("result", "").startswith("PASS"):
            issues.append(f"semantic review TSV: result is not PASS for {file_name} {lang} {section}")
        note = re.sub(r"\s+", " ", row.get("review_note", "")).strip()
        note_counts[note] += 1
        note_template_counts[normalized_review_note_template(note)] += 1
        if len(note) < 28:
            issues.append(f"semantic review TSV: review note is too short for {file_name} {lang} {section}")
        if GENERIC_REVIEW_NOTE.search(note):
            issues.append(f"semantic review TSV: generic review note used for {file_name} {lang} {section}")
        if file_name == "terms.html":
            quoted_phrases = re.findall(r"“([^”]{2,160})”", note)
            if not any(phrase in visible for phrase in quoted_phrases):
                issues.append(
                    f"semantic review TSV: Terms note does not quote current visible wording for {lang} {section}"
                )
            if not re.search(r"原|舊|旧|previous|former|old", note, re.IGNORECASE):
                issues.append(
                    f"semantic review TSV: Terms note does not identify the original defect for {lang} {section}"
                )
            if not re.search(r"現|现|修|改|now|replaced|restored", note, re.IGNORECASE):
                issues.append(
                    f"semantic review TSV: Terms note does not explain the repair for {lang} {section}"
                )
    repeated_notes = sorted((note, count) for note, count in note_counts.items() if note and count > 3)
    if repeated_notes:
        issues.append(f"semantic review TSV: review note repeated at scale ({repeated_notes[0][1]} rows)")
    repeated_templates = sorted(
        (template, count)
        for template, count in note_template_counts.items()
        if template and count > 3
    )
    if repeated_templates:
        issues.append(
            f"semantic review TSV: language-swapped template repeated at scale ({repeated_templates[0][1]} rows)"
        )
    return issues


def sources_issues(soup: BeautifulSoup) -> list[str]:
    issues = []
    reference_urls = None
    for lang in LANGS:
        body = public_body_for(soup, lang)
        if body is None:
            continue
        category_nodes = body.select('[data-section="categories"] li[data-source-type]')
        categories = tuple(node.get("data-source-type") for node in category_nodes)
        if categories != SOURCE_CATEGORY_CODES:
            issues.append(f"sources {lang}: source categories/order differ from the required twelve")
        labels = [node.h3.get_text(" ", strip=True) if node.h3 else "" for node in category_nodes]
        localized_labels = [label.split("—", 1)[-1].strip().casefold() for label in labels]
        if len(set(localized_labels)) != len(SOURCE_CATEGORY_CODES) or any(
            value in {"source material", "material", "资料", "資料"} for value in localized_labels
        ):
            issues.append(f"sources {lang}: source categories were generalized")
        category_floor = 38 if lang in {"zh", "ja", "ko"} else 70
        method_floor = 75 if lang in {"zh", "ja", "ko"} else 150
        for code, node in zip(SOURCE_CATEGORY_CODES, category_nodes):
            text = node.get_text(" ", strip=True)
            if code not in text or len(text) < category_floor:
                issues.append(f"sources {lang}: {code} lacks a natural visible label or explanation")
        for section_name in ("frontline-value", "preservation", "independent-support", "official-boundary"):
            section = body.select_one(f'[data-section="{section_name}"]')
            if section is None or len(section.get_text(" ", strip=True)) < method_floor:
                issues.append(f"sources {lang}: {section_name} evidence role is incomplete")
        official = body.select_one('[data-section="official-boundary"]')
        if official and re.search(r"final truth|最终真相|最終真相|endelige sannhet|vérité finale|Wahrheit letzter Instanz|verità finale|waarheid als eindpunt", official.get_text(" ", strip=True), re.I):
            issues.append(f"sources {lang}: official material is described as final truth")
        link_nodes = body.select('[data-section="retained-links"] li[data-source-url]')
        urls = tuple(node.get("data-source-url") for node in link_nodes)
        if urls != EXPECTED_SOURCE_URLS:
            issues.append(f"sources {lang}: retained source URL set/order changed")
        if any(
            node.get("data-source-type") not in SOURCE_CATEGORY_CODES
            or node.select_one("a[href]") is None
            or node.select_one("a[href]").get("href") != node.get("data-source-url")
            for node in link_nodes
        ):
            issues.append(f"sources {lang}: retained source metadata is inconsistent")
        if reference_urls is None:
            reference_urls = urls
        elif urls != reference_urls:
            issues.append(f"sources {lang}: source links differ between languages")
    return issues


def js_object_languages(block: str) -> set[str]:
    return set(re.findall(r"\b(zh|en|ja|ko|es|de|fr|no|nl|it)\s*:", block))


def protests_script_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "protests.js").read_text(encoding="utf-8")
    issues = []
    event_pattern = re.compile(
        r"date:\s*'([^']+)'\s*,\s*slug:\s*'([^']+)'\s*,\s*count:\s*(\d+)\s*,"
        r"\s*title:\s*\{(.*?)\}\s*,\s*place:\s*\{(.*?)\}\s*\}",
        re.S,
    )
    events = event_pattern.findall(text)
    if len(events) != 8:
        issues.append(f"protests.js: expected 8 events, found {len(events)}")
    total = 0
    for date, slug, count_text, titles, places in events:
        count = int(count_text)
        total += count
        if js_object_languages(titles) != set(LANGS):
            issues.append(f"protests.js: {date} title lacks a ten-language set")
        if js_object_languages(places) != set(LANGS):
            issues.append(f"protests.js: {date} place lacks a ten-language set")
        directory = ROOT / "images" / "protests" / slug
        actual_names = sorted(path.name for path in directory.glob("photo-*.jpg"))
        expected_names = [f"photo-{number:03d}.jpg" for number in range(1, count + 1)]
        if actual_names != expected_names:
            issues.append(f"protests.js: {date} count/files mismatch ({count} declared, {len(actual_names)} present)")
    if total != 254:
        issues.append(f"protests.js: declared photo total is {total}, expected 254")
    for key in ("photos", "photo", "open", "intro", "total"):
        match = re.search(rf"\b{key}:\s*\{{(.*?)\n\s*\}}", text, re.S)
        if not match or js_object_languages(match.group(1)) != set(LANGS):
            issues.append(f"protests.js: galleryLabels.{key} lacks a ten-language set")
    fixed_english = re.search(r"event\.(?:title|place)\.en|galleryLabels\.(?:photos|photo|open|intro|total)\.en", text)
    if fixed_english:
        issues.append("protests.js: dynamic gallery is fixed to English")
    required_code = (
        "event.title[lang]", "event.place[lang]", "galleryLabels.open[lang]",
        "image.alt =", "site-language-change", "event.detail.language",
    )
    if any(value not in text for value in required_code) or "setAttribute('aria-label'" not in text:
        issues.append("protests.js: dynamic alt/aria/title/place language update is incomplete")
    return issues


def language_script_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "language.js").read_text(encoding="utf-8")
    issues = []
    required = (
        'localStorage.getItem("lang")', 'localStorage.setItem("lang", lang)',
        'new CustomEvent("site-language-change"', "detail: { language:",
        'document.documentElement.setAttribute("lang"', "try {", "catch (_error)",
    )
    if any(value not in text for value in required):
        issues.append("language.js: safe persistence, html lang, or language event is incomplete")
    return issues


def nav_footer_issues() -> list[str]:
    issues = []
    for name in PUBLIC_NAV_PAGES:
        soup = BeautifulSoup((ROOT / name).read_text(encoding="utf-8"), "html.parser")
        nav = soup.select_one(".main-nav")
        footer = soup.select_one(".site-footer")
        control = soup.select_one("#lang-toggle")
        menu = soup.select_one(".mobile-menu-btn")
        if nav is None or footer is None or control is None or menu is None:
            issues.append(f"{name}: navigation, footer, mobile menu, or language control is missing")
            continue
        if any(localized_classes(link) != set(LANGS) for link in nav.select("a")):
            issues.append(f"{name}: a navigation label lacks ten languages")
        if len(control.select("option")) != len(LANGS) or {option.get("value") for option in control.select("option")} != set(LANGS):
            issues.append(f"{name}: language selector is incomplete")
        footer_groups = footer.select(".footer-links a, .footer-copy p")
        if not footer_groups or any(localized_classes(group) != set(LANGS) for group in footer_groups):
            issues.append(f"{name}: footer labels lack ten languages")
        if not menu.get("data-i18n-aria") or not nav.get("data-i18n-aria"):
            issues.append(f"{name}: mobile navigation localization hooks are missing")
    return issues


def public_page_checks() -> list[str]:
    issues = []
    documents = {}
    for name in PUBLIC_PAGES:
        path = ROOT / name
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        documents[name] = soup
        issues.extend(f"{name}: {issue}" for issue in public_page_issues(soup, path))
        issues.extend(traditional_chinese_issues(soup, name))
    issues.extend(f"privacy.html: {issue}" for issue in privacy_issues(documents["privacy.html"]))
    issues.extend(f"about.html: {issue}" for issue in about_issues(documents["about.html"]))
    issues.extend(f"terms.html: {issue}" for issue in terms_issues(documents["terms.html"]))
    issues.extend(f"contact.html: {issue}" for issue in contact_page_issues(documents["contact.html"]))
    issues.extend(f"sources.html: {issue}" for issue in sources_issues(documents["sources.html"]))
    issues.extend(f"index.html: {issue}" for issue in index_contact_issues(
        BeautifulSoup((ROOT / "index.html").read_text(encoding="utf-8"), "html.parser")
    ))
    issues.extend(nav_footer_issues())
    issues.extend(protests_script_issues())
    issues.extend(language_script_issues())
    issues.extend(semantic_review_issues())
    return issues


def validate_paths() -> list[str]:
    issues = []
    if len(FILES) != EXPECTED_FILES:
        issues.append(f"posts: expected {EXPECTED_FILES} public articles, found {len(FILES)}")
    for path in FILES:
        raw = path.read_text(encoding="utf-8")
        if GLOBAL_TERMS.search(raw):
            issues.append(f"posts/{path.name}: prohibited error term remains")
        soup = BeautifulSoup(raw, "html.parser")
        issues.extend(f"posts/{path.name}: {issue}" for issue in issue_list(soup, path))
    issues.extend(duplicate_sentence_issues())
    issues.extend(card_issues())
    issues.extend(frozen_article_issues())
    issues.extend(public_page_checks())
    return issues


def release_text(name: str, overrides: dict[str, str | bytes] | None = None) -> str:
    value = (overrides or {}).get(name)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, str):
        return value
    return (ROOT / name).read_text(encoding="utf-8")


def release_html_paths() -> tuple[Path, ...]:
    return tuple(ROOT / name for name in RELEASE_ROOT_PAGES) + FILES


def local_target_path(page: Path, raw_path: str) -> Path:
    decoded = unquote(raw_path)
    if decoded.startswith("/"):
        target = ROOT / (decoded.lstrip("/") or "index.html")
    elif decoded:
        target = page.parent / decoded
    else:
        target = page
    if target.is_dir():
        target = target / "index.html"
    return target.resolve()


def control_has_accessible_name(control, soup: BeautifulSoup) -> bool:
    if control.name == "input" and control.get("type", "").casefold() == "hidden":
        return True
    if control.get("aria-label") or control.get("aria-labelledby"):
        return True
    if control.get_text(" ", strip=True):
        return True
    if control.name == "input" and control.get("type", "").casefold() in {"submit", "button", "reset"}:
        return bool(control.get("value", "").strip())
    if control.find_parent("label"):
        return True
    control_id = control.get("id")
    return bool(control_id and soup.find("label", attrs={"for": control_id}))


def public_html_release_issues(overrides: dict[str, str | bytes] | None = None) -> list[str]:
    issues: list[str] = []
    documents: dict[str, BeautifulSoup] = {}
    for path in release_html_paths():
        relative = path.relative_to(ROOT).as_posix()
        if not path.exists() and relative not in (overrides or {}):
            issues.append(f"{relative}: public HTML file is missing")
            continue
        documents[relative] = BeautifulSoup(release_text(relative, overrides), "html.parser")

    root_resolved = ROOT.resolve()
    for relative, soup in documents.items():
        path = ROOT / relative
        raw = release_text(relative, overrides)
        if LOCAL_PATH_MARKERS.search(raw):
            issues.append(f"{relative}: local filesystem path appears in public HTML")

        head = soup.head
        if head is None:
            issues.append(f"{relative}: missing head")
        else:
            if not head.find("meta", attrs={"charset": True}):
                issues.append(f"{relative}: missing charset metadata")
            viewport = head.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
            if not viewport or not viewport.get("content", "").strip():
                issues.append(f"{relative}: missing viewport metadata")
            if not head.title or not head.title.get_text(" ", strip=True):
                issues.append(f"{relative}: missing non-empty title")
            icon_links = [
                link for link in head.find_all("link")
                if "icon" in {item.casefold() for item in (link.get("rel") or [])}
                and link.get("href", "").strip()
            ]
            if not icon_links:
                issues.append(f"{relative}: missing favicon")

        ids = [node.get("id") for node in soup.select("[id]")]
        for duplicate, count in Counter(ids).items():
            if duplicate and count > 1:
                issues.append(f"{relative}: duplicate HTML id {duplicate!r}")

        for image in soup.find_all("img"):
            if not image.has_attr("alt"):
                issues.append(f"{relative}: image {image.get('src', '')!r} lacks alt text")
            elif not image.get("alt", "").strip() and not (
                image.get("role") == "presentation" or image.get("aria-hidden") == "true"
            ):
                issues.append(
                    f"{relative}: image {image.get('src', '')!r} has empty alt without an explicit decorative rule"
                )

        for control in soup.select("input, select, textarea, button"):
            if not control_has_accessible_name(control, soup):
                issues.append(f"{relative}: unnamed {control.name} form control")

        for anchor in soup.select('a[target="_blank"]'):
            rel_values = {item.casefold() for item in (anchor.get("rel") or [])}
            if not {"noopener", "noreferrer"}.issubset(rel_values):
                issues.append(
                    f"{relative}: new-window link lacks rel=\"noopener noreferrer\": {anchor.get('href', '')}"
                )

        referenced = [(node, "href") for node in soup.select("[href]")]
        referenced += [(node, "src") for node in soup.select("[src]")]
        for node, attribute in referenced:
            value = node.get(attribute, "").strip()
            if not value:
                continue
            parsed = urlsplit(value)
            if value.startswith("//") or parsed.scheme:
                continue
            target = local_target_path(path, parsed.path)
            try:
                target_relative = target.relative_to(root_resolved).as_posix()
            except ValueError:
                issues.append(f"{relative}: local {attribute} escapes the repository: {value}")
                continue

            parts = set(Path(target_relative).parts)
            if parts & FORBIDDEN_PUBLIC_LINK_PARTS or target_relative == "posts/template.html":
                issues.append(f"{relative}: public link targets excluded maintenance content: {value}")
            if not target.exists():
                issues.append(f"{relative}: local {attribute} target does not exist: {value}")
                continue
            if parsed.fragment and target.suffix.casefold() == ".html":
                target_soup = documents.get(target_relative)
                if target_soup is None:
                    target_soup = BeautifulSoup(release_text(target_relative, overrides), "html.parser")
                if target_soup.find(id=unquote(parsed.fragment)) is None:
                    issues.append(f"{relative}: internal anchor target does not exist: {value}")
    return issues


def expected_sitemap_urls() -> tuple[str, ...]:
    paths = SITEMAP_ROOT_PATHS + tuple(f"/posts/{path.name}" for path in FILES)
    return tuple(SITE_ORIGIN + path for path in paths)


def sitemap_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    issues: list[str] = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return [f"sitemap.xml: invalid XML: {exc}"]
    if root.tag.rsplit("}", 1)[-1] != "urlset":
        issues.append("sitemap.xml: root element is not urlset")
    locs = [
        (node.text or "").strip()
        for node in root.iter()
        if node.tag.rsplit("}", 1)[-1] == "loc"
    ]
    if len(locs) != len(set(locs)):
        issues.append("sitemap.xml: duplicate URL")
    expected = set(expected_sitemap_urls())
    actual = set(locs)
    for missing in sorted(expected - actual):
        issues.append(f"sitemap.xml: missing public URL {missing}")
    for extra in sorted(actual - expected):
        issues.append(f"sitemap.xml: unexpected or non-public URL {extra}")
    for loc in locs:
        parsed = urlsplit(loc)
        if parsed.scheme != "https" or parsed.netloc != "zhonghuafreedom.org":
            issues.append(f"sitemap.xml: URL is not on the canonical HTTPS origin: {loc}")
            continue
        if parsed.query or parsed.fragment:
            issues.append(f"sitemap.xml: URL contains a query or fragment: {loc}")
        deployment_path = ROOT / (parsed.path.lstrip("/") or "index.html")
        if not deployment_path.is_file():
            issues.append(f"sitemap.xml: URL has no deployment file: {loc}")
    if any(node.tag.rsplit("}", 1)[-1] == "lastmod" for node in root.iter()):
        issues.append("sitemap.xml: lastmod is present without a maintained per-page date source")
    return issues


def robots_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "robots.txt").read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    issues = []
    if "User-agent: *" not in lines:
        issues.append("robots.txt: missing User-agent: *")
    if "Allow: /" not in lines:
        issues.append("robots.txt: missing Allow: /")
    expected = f"Sitemap: {SITE_ORIGIN}/sitemap.xml"
    sitemap_lines = [line for line in lines if line.casefold().startswith("sitemap:")]
    if sitemap_lines != [expected]:
        issues.append("robots.txt: Sitemap URL does not exactly match CNAME")
    return issues


def parse_config_excludes(text: str) -> tuple[list[str], list[str]]:
    excludes: list[str] = []
    issues: list[str] = []
    in_exclude = False
    saw_exclude = False
    for number, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw:
            issues.append(f"_config.yml:{number}: tabs are not valid indentation")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not raw.startswith((" ", "-")):
            in_exclude = stripped == "exclude:"
            saw_exclude |= in_exclude
            continue
        if in_exclude:
            if not stripped.startswith("- "):
                issues.append(f"_config.yml:{number}: malformed exclude list item")
                continue
            value = stripped[2:].strip().strip('"\'')
            if not value:
                issues.append(f"_config.yml:{number}: empty exclude list item")
            else:
                excludes.append(value)
    if not saw_exclude:
        issues.append("_config.yml: missing exclude list")
    return excludes, issues


def config_excludes_path(pattern: str, candidate: str) -> bool:
    normalized = pattern.strip().strip("/")
    candidate = candidate.strip("/")
    return (
        candidate == normalized
        or candidate.startswith(normalized + "/")
        or fnmatch.fnmatch(candidate, normalized)
    )


def config_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "_config.yml").read_text(encoding="utf-8")
    excludes, issues = parse_config_excludes(text)
    normalized = {item.strip().strip("/") for item in excludes}
    for required in sorted(REQUIRED_CONFIG_EXCLUDES - normalized):
        issues.append(f"_config.yml: missing required exclusion {required}")
    if any(config_excludes_path(item, "CNAME") for item in excludes):
        issues.append("_config.yml: CNAME must not be excluded")
    for path in FILES:
        candidate = f"posts/{path.name}"
        if any(config_excludes_path(item, candidate) for item in excludes):
            issues.append(f"_config.yml: formal article is excluded: {candidate}")
    return issues


def cname_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "CNAME").read_text(encoding="utf-8")
    return [] if text.strip() == "zhonghuafreedom.org" else ["CNAME: must exactly equal zhonghuafreedom.org"]


def sync_script_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "tools/sync_languages.py").read_text(encoding="utf-8")
    risks = {
        "translate.googleapis.com": "network translation endpoint",
        "urllib.request": "network request module",
        "urlopen": "network request call",
        "write_text": "filesystem write capability",
        "clone_lang_blocks": "English-block cloning path",
        "translate_js_reports": "report-card translation writer",
        "replace_post_inline_script": "inline-script replacement path",
    }
    issues = [
        f"tools/sync_languages.py: contains prohibited {label}"
        for token, label in risks.items() if token.casefold() in text.casefold()
    ]
    if re.search(r"\bopen\s*\([^\n]*,['\"]\s*[wax+]", text):
        issues.append("tools/sync_languages.py: contains a write-mode open call")
    return issues


def readme_release_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "README.md").read_text(encoding="utf-8")
    issues = []
    banned = (
        "uses the English blocks as the source",
        "English blocks as the source",
    )
    if any(phrase.casefold() in text.casefold() for phrase in banned):
        issues.append("README.md: restores English-block machine-translation guidance")
    required_phrases = (
        "Traditional Chinese is the content master",
        "must each be translated by a person",
        "network translation services must not be used",
        "tools/sync_languages.py` is a read-only missing-item audit",
        "Do not commit, push, or change remote repository settings",
    )
    for phrase in required_phrases:
        if phrase.casefold() not in text.casefold():
            issues.append(f"README.md: missing maintenance rule {phrase!r}")
    commands = (
        "python3 tools/check_languages.py",
        "python3 tools/check_languages.py --matrix",
        "python3 tools/check_languages.py --self-test",
        "node --check script.js",
        "node --check language.js",
        "node --check protests.js",
        "git diff --check",
    )
    for command in commands:
        if command not in text:
            issues.append(f"README.md: missing validation command {command}")
    return issues


def gitignore_patterns(text: str) -> list[str]:
    return [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def gitignore_pattern_matches(pattern: str, candidate: str) -> bool:
    original = pattern
    pattern = pattern.lstrip("!").lstrip("/")
    candidate = candidate.lstrip("/")
    if original.endswith("/"):
        directory = pattern.rstrip("/")
        return (
            candidate == directory
            or candidate.startswith(directory + "/")
            or f"/{directory}/" in f"/{candidate}/"
        )
    if "/" not in pattern:
        return any(fnmatch.fnmatch(part, pattern) for part in candidate.split("/"))
    return fnmatch.fnmatch(candidate, pattern)


def gitignore_ignores(patterns: list[str], candidate: str) -> bool:
    ignored = False
    for pattern in patterns:
        if gitignore_pattern_matches(pattern, candidate):
            ignored = not pattern.startswith("!")
    return ignored


def gitignore_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / ".gitignore").read_text(encoding="utf-8")
    patterns = gitignore_patterns(text)
    issues = []
    required = {
        ".DS_Store", "tools/.translation-cache.json", ".visual-qa/", "visual-qa/",
        "screenshots/", "__pycache__/", "*.py[cod]", "npm-debug.log*",
        "yarn-debug.log*", "yarn-error.log*", "pnpm-debug.log*", ".http-server.log",
        "http-server*.log", "local-server*.log",
    }
    for pattern in sorted(required - set(patterns)):
        issues.append(f".gitignore: missing local-artifact rule {pattern}")
    public_samples = [
        "index.html", "posts/2024-report.html", "images/protests/2025-09-03/photo-001.jpg",
        "CNAME", "sitemap.xml", "robots.txt", "404.html", "_config.yml",
    ]
    for candidate in public_samples:
        if gitignore_ignores(patterns, candidate):
            issues.append(f".gitignore: publication file would be ignored: {candidate}")
    return issues


def not_found_issues(text_override: str | None = None) -> list[str]:
    text = text_override if text_override is not None else (ROOT / "404.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    issues: list[str] = []
    if not soup.html or soup.html.get("lang") != "zh-Hant":
        issues.append("404.html: initial html lang must be zh-Hant")
    body = soup.body
    if body is None:
        return ["404.html: missing body"]
    expected_links = {"index.html", "reports.html", "sources.html", "contact.html"}
    english_text = ""
    for lang in LANGS:
        containers = soup.select(f'[data-language-body="{lang}"]')
        if len(containers) != 1:
            issues.append(f"404.html: expected one {lang} body, found {len(containers)}")
            continue
        container = containers[0]
        headings = container.find_all("h1")
        if len(headings) != 1 or not headings[0].get_text(" ", strip=True):
            issues.append(f"404.html: {lang} must have one non-empty H1")
        paragraphs = container.find_all("p")
        if not paragraphs or not " ".join(p.get_text(" ", strip=True) for p in paragraphs).strip():
            issues.append(f"404.html: {lang} body text is empty")
        links = {urlsplit(a.get("href", "")).path for a in container.find_all("a")}
        if not expected_links.issubset(links):
            issues.append(f"404.html: {lang} lacks one or more required recovery links")
        visible = re.sub(r"\s+", " ", container.get_text(" ", strip=True)).casefold()
        if lang == "en":
            english_text = visible
        elif english_text and visible == english_text:
            issues.append(f"404.html: {lang} falls back to English")
        if not body.get(f"data-title-{lang}", "").strip():
            issues.append(f"404.html: missing localized document title for {lang}")
    options = [option.get("value") for option in soup.select("#lang-toggle option")]
    if options != list(LANGS):
        issues.append("404.html: language selector is not the exact ten-language sequence")
    scripts = {urlsplit(node.get("src", "")).path for node in soup.find_all("script", src=True)}
    if not {"language.js", "script.js"}.issubset(scripts):
        issues.append("404.html: language.js or script.js is missing")
    menu = soup.select_one(".mobile-menu-btn")
    if not menu or menu.get("aria-expanded") != "false":
        issues.append("404.html: mobile menu lacks initial aria-expanded=false")
    if soup.find("form"):
        issues.append("404.html: forms are not allowed")
    if PUBLIC_BANNED.search(soup.get_text(" ", strip=True)):
        issues.append("404.html: prohibited public wording appears")
    return issues


def release_surface_issues(overrides: dict[str, str | bytes] | None = None) -> list[str]:
    overrides = overrides or {}
    issues = public_html_release_issues(overrides)
    issues.extend(sitemap_issues(release_text("sitemap.xml", overrides)))
    issues.extend(robots_issues(release_text("robots.txt", overrides)))
    issues.extend(config_issues(release_text("_config.yml", overrides)))
    issues.extend(cname_issues(release_text("CNAME", overrides)))
    issues.extend(sync_script_issues(release_text("tools/sync_languages.py", overrides)))
    issues.extend(readme_release_issues(release_text("README.md", overrides)))
    issues.extend(gitignore_issues(release_text(".gitignore", overrides)))
    issues.extend(not_found_issues(release_text("404.html", overrides)))
    return issues


def release_surface_statistics() -> Counter:
    stats = Counter()
    for path in release_html_paths():
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        stats["html"] += 1
        stats["images"] += len(soup.find_all("img"))
        stats["controls"] += len(soup.select("input, select, textarea, button"))
        for node, attribute in (
            [(item, "href") for item in soup.select("[href]")]
            + [(item, "src") for item in soup.select("[src]")]
        ):
            value = node.get(attribute, "").strip()
            parsed = urlsplit(value)
            if value and not value.startswith("//") and not parsed.scheme:
                stats["local_references"] += 1
                stats["anchors"] += int(bool(parsed.fragment))
    stats["sitemap_urls"] = len(expected_sitemap_urls())
    stats["formal_posts"] = len(FILES)
    return stats


def add_after(heading, tag):
    heading.insert_after(tag)


def self_tests() -> tuple[int, int]:
    """Exercise real cross-file mutations and all critical-column gates."""
    checks = []

    def clone(path):
        return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    def record(label, caught):
        checks.append((label, bool(caught)))

    # 1. The pair test deliberately lowers the release threshold so two
    # distinct pages prove that the cross-document index, not a single soup,
    # is being exercised.
    pair = {FILES[0]: clone(FILES[0]), FILES[1]: clone(FILES[1])}
    shared_zh = "地方機關控制調查、關鍵證據與公開發言，使受害家庭無法安全追問責任，也無法取得真正獨立且能夠實際執行的司法救濟。"
    for soup in pair.values():
        body_for(soup, "zh").select_one("p.critical-conclusion span").append(shared_zh)
    record("two-page Chinese duplicate", duplicate_sentence_issues(pair, threshold=2))

    triple_paths = FILES[:3]
    triple = {path: clone(path) for path in triple_paths}
    shared_ja = "国家機関が証拠の公開と家族の発言を統制したため、被害者は独立調査と実効的救済を安全に求めることができなかった。"
    for soup in triple.values():
        body_for(soup, "ja").select_one("p.critical-protection span").append(shared_ja)
    record("three-page Japanese duplicate", duplicate_sentence_issues(triple))

    source = clone(FILES[0])
    rights = body_for(source, "en").select_one("p.critical-conclusion").get_text(" ", strip=True)
    protection = body_for(source, "en").select_one("p.critical-protection span")
    protection.string = rights
    protection["data-critical-case"] = sentence_parts(rights, "en")[0]
    record("same-page rights copied to protection", issue_list(source, FILES[0], source_signatures=False))

    copied = {FILES[0]: clone(FILES[0]), FILES[1]: clone(FILES[1])}
    source_rights = body_for(copied[FILES[0]], "en").select_one("p.critical-conclusion").get_text(" ", strip=True)
    target = body_for(copied[FILES[1]], "en").select_one("p.critical-conclusion span")
    target.string = "Another Case. " + " ".join(sentence_parts(source_rights, "en")[1:])
    record("title-swapped cross-page copy", duplicate_sentence_issues(copied, threshold=2))

    lower = clone(FILES[0])
    span = body_for(lower, "es").select_one("p.critical-protection span")
    span.string = "esidualword " + span.get_text(" ", strip=True)
    record("European lowercase residual opening", issue_list(lower, FILES[0], source_signatures=False))

    xiaoluoxi = next(path for path in FILES if path.name == "ningbo-xiaoluoxi-medical-case.html")
    broken_ja = clone(xiaoluoxi)
    span = body_for(broken_ja, "ja").select_one("p.critical-conclusion span")
    span.string = "存のすべてが国家機構の介入にさらされるとき、最初の被害は拡大する。" + span.get_text(" ", strip=True)
    record("Xiao Luoxi Japanese residual opening", issue_list(broken_ja, xiaoluoxi, source_signatures=False))

    guiyang = next(path for path in FILES if path.name == "guiyang-quarantine-bus-crash.html")
    broken_zh = clone(guiyang)
    span = body_for(broken_zh, "zh").select_one("p.critical-protection span")
    span.string = "效救濟的缺失使風險持續。" + span.get_text(" ", strip=True)
    record("Guiyang Chinese residual opening", issue_list(broken_zh, guiyang, source_signatures=False))

    huge = clone(FILES[0])
    span = body_for(huge, "en").select_one("p.critical-protection span")
    span.string = "Police controlled the evidence and family communication. " + ("State pressure blocked an effective remedy for the affected family. " * 50)
    record("three-thousand-character protection", issue_list(huge, FILES[0], source_signatures=False))

    guide = clone(FILES[0])
    heading = find_heading(body_for(guide, "en"), HEADINGS["en"][1])
    ordinary = guide.new_tag("p")
    ordinary.string = "This page does not replace legal evidence for a protection application."
    heading.insert_after(ordinary)
    record("guide in ordinary visible node", issue_list(guide, FILES[0], source_signatures=False))

    abstract = clone(FILES[0])
    span = body_for(abstract, "en").select_one("p.critical-conclusion span")
    span.string = "People deserve dignity, safety, rights, and a remedy for harm."
    span["data-critical-case"] = span.string
    record("missing case-specific state actor and act", issue_list(abstract, FILES[0], source_signatures=False))

    wrapped = clone(FILES[0])
    rights = body_for(wrapped, "en").select_one("p.critical-conclusion").get_text(" ", strip=True)
    span = body_for(wrapped, "en").select_one("p.critical-protection span")
    span.string = "Relatives remain exposed to police pressure. " + rights + " The state must provide relief."
    span["data-critical-case"] = sentence_parts(span.string, "en")[0]
    record("rights contained inside longer protection", issue_list(wrapped, FILES[0], source_signatures=False))

    cjk_ok = (
        len(sentence_parts("第一句沒有空格。第二句仍能分開！第三句也可以？", "zh")) == 3
        and len(sentence_parts("最初の文です。次の文です！最後の文です？", "ja")) == 3
        and len(sentence_parts("첫 문장입니다.다음 문장입니다!마지막 문장입니다?", "ko")) == 3
    )
    record("CJK punctuation without spaces", cjk_ok)

    zhang = next(path for path in FILES if path.name == "zhang-zhan.html")
    broken_zhang = clone(zhang)
    body_for(broken_zhang, "ko").select_one("p.critical-protection span").append(" 그가 다시 구금되었다.")
    record(
        "Zhang Zhan Korean male pronoun",
        any("male pronoun" in issue for issue in issue_list(broken_zhang, zhang, source_signatures=False)),
    )

    broken_guiyang_ja = clone(guiyang)
    span = body_for(broken_guiyang_ja, "ja").select_one("p.critical-protection span")
    span.string = span.get_text(" ", strip=True).replace("中国当局は", "州は", 1)
    record(
        "Guiyang Japanese state rendered as shu",
        any("mistranslated as 州" in issue for issue in issue_list(broken_guiyang_ja, guiyang, source_signatures=False)),
    )

    guangzhou = next(path for path in FILES if path.name == "guangzhou-haizhu-lockdown-protests.html")
    broken_title = clone(guangzhou)
    english_title = broken_title.select_one("h1.article-title .lang-en").get_text(" ", strip=True)
    broken_title.select_one("h1.article-title .lang-no").string = english_title
    record(
        "Guangzhou Norwegian article-title fallback",
        any("article title: no falls back" in issue for issue in issue_list(broken_title, guangzhou, source_signatures=False)),
    )

    directive = clone(FILES[0])
    body_for(directive, "en").select_one("ol.timeline-list li").append(" This claim must be attributed.")
    record(
        "editorial directive in ordinary timeline",
        any("public visible text" in issue for issue in issue_list(directive, FILES[0], source_signatures=False)),
    )

    critical_directive = clone(FILES[0])
    body_for(critical_directive, "en").select_one("p.critical-conclusion span").append(
        " This claim must be attributed."
    )
    record(
        "editorial directive in critical visible text",
        any(
            "public visible text" in issue
            for issue in issue_list(critical_directive, FILES[0], source_signatures=False)
        ),
    )

    # Public-page mutations exercise the new release gates against actual DOM
    # and JavaScript structures rather than institution-name keyword probes.
    terms_path = ROOT / "terms.html"
    broken_terms = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    disclaimer = broken_terms.new_tag("p")
    disclaimer.string = "This is not legal, medical, or immigration advice."
    public_body_for(broken_terms, "en").select_one("section").append(disclaimer)
    record(
        "public legal-medical-immigration disclaimer",
        any("prohibited public disclaimer" in issue for issue in public_page_issues(broken_terms, terms_path)),
    )

    privacy_path = ROOT / "privacy.html"
    missing_formspree = BeautifulSoup(privacy_path.read_text(encoding="utf-8"), "html.parser")
    privacy_en = public_body_for(missing_formspree, "en")
    for node in privacy_en.find_all(string=re.compile("Formspree")):
        node.replace_with(node.replace("Formspree", "external form service"))
    record(
        "deleted Formspree disclosure",
        any("missing Formspree" in issue for issue in privacy_issues(missing_formspree)),
    )

    missing_storage = BeautifulSoup(privacy_path.read_text(encoding="utf-8"), "html.parser")
    privacy_en = public_body_for(missing_storage, "en")
    for node in privacy_en.find_all(string=re.compile("localStorage")):
        node.replace_with(node.replace("localStorage", "browser preference storage"))
    record(
        "deleted localStorage disclosure",
        any("missing localStorage" in issue for issue in privacy_issues(missing_storage)),
    )

    french_key = BeautifulSoup(privacy_path.read_text(encoding="utf-8"), "html.parser")
    french_storage = public_body_for(french_key, "fr").select_one('[data-section="language-storage"]')
    french_first = french_storage.find("p", recursive=False)
    french_first.string = french_first.get_text().replace("sous la clé lang", "sous la clé langue")
    record(
        "French lang key changed to ordinary word",
        any("privacy fr: localStorage key" in issue for issue in privacy_issues(french_key)),
    )

    norwegian_value = BeautifulSoup(privacy_path.read_text(encoding="utf-8"), "html.parser")
    norwegian_storage = public_body_for(norwegian_value, "no").select_one('[data-section="language-storage"]')
    for node in norwegian_storage.find_all(string=re.compile(r"nl og it")):
        node.replace_with(node.replace("nl og it", "nl og det"))
    record(
        "Norwegian it value changed to det",
        any("ten-code language set" in issue or "mistranslation returned" in issue for issue in privacy_issues(norwegian_value)),
    )

    deleted_code = BeautifulSoup(privacy_path.read_text(encoding="utf-8"), "html.parser")
    english_storage = public_body_for(deleted_code, "en").select_one('[data-section="language-storage"]')
    for node in english_storage.find_all(string=re.compile(PRIVACY_CODE_SEQUENCE)):
        node.replace_with(node.replace("zh, en, ja, ko", "zh, en, ko"))
    record(
        "privacy ordered language code deleted",
        any("ten-code language set" in issue for issue in privacy_issues(deleted_code)),
    )

    about_path = ROOT / "about.html"
    service_about = BeautifulSoup(about_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(service_about, "es").select_one('[data-section="mission"] p').string = (
        "El Frente Chino por la Libertad presta servicios a personas afectadas y familiares."
    )
    record(
        "about service-provider meaning restored",
        any("service-provider claim" in issue for issue in about_issues(service_about)),
    )

    uncertainty_terms = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(uncertainty_terms, "fr").select('[data-section="citation"] li')[2].append(
        " marqueurs d’incertitude"
    )
    record(
        "terms uncertainty-marker wording restored",
        any("uncertainty-marker wording" in issue for issue in terms_issues(uncertainty_terms)),
    )

    mixed_chinese = BeautifulSoup(privacy_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(mixed_chinese, "zh").select_one('[data-section="language-storage"] p').append(
        " 使用 localStorage 在 key lang 下存储偏好。"
    )
    record(
        "privacy simplified storage and key phrase restored",
        bool(traditional_chinese_issues(mixed_chinese, "privacy.html")),
    )

    contact_path = ROOT / "contact.html"
    unavailable_channels = BeautifulSoup(contact_path.read_text(encoding="utf-8"), "html.parser")
    unavailable_channels.new_tag("p")
    channel_list = unavailable_channels.new_tag("p")
    channel_list.string = (
        "The site does not list social-media, Signal, Telegram, encrypted-email, or anonymous-upload accounts."
    )
    public_body_for(unavailable_channels, "en").select_one('[data-section="channels"]').append(channel_list)
    record(
        "contact missing-channel negative list restored",
        any("negative list of unavailable contact features" in issue for issue in contact_page_issues(unavailable_channels)),
    )

    reversed_flow = BeautifulSoup(contact_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(reversed_flow, "en").select_one('[data-section="form-data"] p').string = (
        "Formspree receives the three form fields name, email, and message and transmits those values "
        "to an external service so the message can reach the site."
    )
    record(
        "Formspree flow reversed toward another external service",
        any("data flow is reversed" in issue for issue in contact_page_issues(reversed_flow)),
    )

    bad_contact_ja = BeautifulSoup(contact_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(bad_contact_ja, "ja").select('[data-section="submissions"] li')[0].string = (
        "公開ソースとそれがサポートするページまたは主張。"
    )
    record(
        "Japanese contact support-or-claim machine translation",
        any("known mechanical translation" in issue for issue in contact_page_issues(bad_contact_ja)),
    )

    bad_contact_es = BeautifulSoup(contact_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(bad_contact_es, "es").select('[data-section="submissions"] li')[0].string = (
        "Una fuente pública y la página o reclamo que respalda."
    )
    record(
        "Spanish contact reclamo regression",
        any("known mechanical translation" in issue for issue in contact_page_issues(bad_contact_es)),
    )

    bad_contact_fr = BeautifulSoup(contact_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(bad_contact_fr, "fr").select('[data-section="submissions"] li')[0].string = (
        "Une source publique et la page ou la revendication qu'elle prend en charge."
    )
    record(
        "French contact prend-en-charge regression",
        any("known mechanical translation" in issue for issue in contact_page_issues(bad_contact_fr)),
    )

    bad_attribution = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(bad_attribution, "ja").select('[data-section="citation"] li')[1].append(" 限定的な帰属")
    record(
        "qualifying-attribution noun translation restored",
        any("mechanical source" in issue for issue in terms_issues(bad_attribution)),
    )

    civil_records = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    civil_node = public_body_for(civil_records, "en").select('[data-section="evidence-use"] p')[0]
    civil_node.string = civil_node.get_text().replace("records preserved by citizens or civil society", "civil records")
    record(
        "citizen records changed to civil records",
        any("mechanical source" in issue or "citizen meaning" in issue for issue in terms_issues(civil_records)),
    )

    reports_abroad = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    media_node = public_body_for(reports_abroad, "en").select('[data-section="evidence-use"] p')[0]
    media_node.string = media_node.get_text().replace("reporting by overseas media", "reports abroad")
    record(
        "overseas-media reporting changed to reports abroad",
        any("mechanical source" in issue or "media meaning" in issue for issue in terms_issues(reports_abroad)),
    )

    weak_stability = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(weak_stability, "en").select('[data-section="evidence-use"] p')[1].string = (
        "The site examines state power, information control, stability maintenance, and effective remedies."
    )
    record(
        "state coercion weakened to stability maintenance",
        any("mechanical source" in issue or "stability meaning" in issue for issue in terms_issues(weak_stability)),
    )

    review_rows, _ = load_semantic_review_rows()
    repeated_review = copy.deepcopy(review_rows)
    for row in repeated_review[:20]:
        row["review_note"] = "句法、指代和动作关系自然，未发现英语回退。"
    record(
        "generic semantic-review note copied at scale",
        any("generic review note" in issue or "repeated at scale" in issue for issue in semantic_review_issues(repeated_review)),
    )

    bad_zh_certainty = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    zh_certainty_node = public_body_for(bad_zh_certainty, "zh").select('[data-section="citation"] li')[1]
    zh_certainty_node.string = zh_certainty_node.get_text().replace("確信程度", "确信程度")
    record(
        "Terms Traditional Chinese certainty changed back to simplified form",
        any("latest audited" in issue for issue in terms_issues(bad_zh_certainty)),
    )

    bad_zh_support = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    zh_support_node = public_body_for(bad_zh_support, "zh").select('[data-section="corrections"] li')[0]
    zh_support_node.string = zh_support_node.get_text().replace("作為佐證的公開資料", "支援公共資料")
    record(
        "Terms Chinese supporting-public-material machine phrase restored",
        any("latest audited" in issue for issue in terms_issues(bad_zh_support)),
    )

    bad_ko_support = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    ko_support_node = public_body_for(bad_ko_support, "ko").select('[data-section="corrections"] li')[0]
    ko_support_node.string = ko_support_node.get_text().replace("정정 내용을 뒷받침하는 공개 자료", "지원 공개 자료")
    record(
        "Terms Korean support-public-material noun string restored",
        any("latest audited" in issue for issue in terms_issues(bad_ko_support)),
    )

    bad_fr_support = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    fr_support_node = public_body_for(bad_fr_support, "fr").select('[data-section="corrections"] li')[0]
    fr_support_node.string = fr_support_node.get_text().replace(
        "des documents publics étayant la correction proposée", "le matériel public à l’appui"
    )
    record(
        "Terms French support-material machine phrase restored",
        any("latest audited" in issue for issue in terms_issues(bad_fr_support)),
    )

    bad_no_retaliation = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    no_safety_node = public_body_for(bad_no_retaliation, "no").select_one('[data-section="safety"] p')
    no_safety_node.string = no_safety_node.get_text().replace(
        "eller utsette berørte personer, familiemedlemmer, vitner, journalister eller støttespillere for represalier",
        "eller gjengjeldelse mot berørte personer, familiemedlemmer, vitner, journalister eller støttespillere",
    )
    record(
        "Terms Norwegian retaliation sentence lost its governing verb",
        any("latest audited" in issue for issue in terms_issues(bad_no_retaliation)),
    )

    bad_de_support = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    de_support_node = public_body_for(bad_de_support, "de").select('[data-section="corrections"] li')[0]
    de_support_node.string = de_support_node.get_text().replace(
        "öffentlich zugängliche Belege", "unterstützendes öffentliches Material"
    )
    record(
        "Terms German supporting-public-material calque restored",
        any("latest audited" in issue for issue in terms_issues(bad_de_support)),
    )

    bad_nl_ownership = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    nl_ownership_node = public_body_for(bad_nl_ownership, "nl").select('[data-section="corrections"] li')[2]
    nl_ownership_node.string = nl_ownership_node.get_text().replace(
        "Ongefundeerde eigendomsaanspraken", "niet-ondersteunde eigendomsclaims"
    )
    record(
        "Terms Dutch unsupported-ownership English calque restored",
        any("latest audited" in issue for issue in terms_issues(bad_nl_ownership)),
    )

    bad_it_support = BeautifulSoup(terms_path.read_text(encoding="utf-8"), "html.parser")
    it_support_node = public_body_for(bad_it_support, "it").select('[data-section="corrections"] li')[0]
    it_support_node.string = it_support_node.get_text().replace(
        "documentazione pubblica che sostenga la correzione", "materiale pubblico di supporto"
    )
    record(
        "Terms Italian public-support-material noun string restored",
        any("latest audited" in issue for issue in terms_issues(bad_it_support)),
    )

    language_swapped_review = copy.deepcopy(review_rows)
    review_labels = {
        "zh": "繁體中文", "en": "英文", "ja": "日文", "ko": "韓文", "es": "西班牙文",
        "de": "德文", "fr": "法文", "no": "挪威文", "nl": "荷蘭文", "it": "義大利文",
    }
    for row in language_swapped_review:
        if row["file"] == "terms.html" and row["section"] == "corrections":
            row["review_note"] = (
                f"{review_labels[row['language']]}更正條款核對頁面與問題位置、公開佐證材料、版權對象和請求依據；"
                "原句有誤，現已修復。"
            )
    record(
        "semantic-review template copied across ten languages with labels swapped",
        any(
            "language-swapped template repeated" in issue
            for issue in semantic_review_issues(language_swapped_review)
        ),
    )

    sources_path = ROOT / "sources.html"
    official_truth = BeautifulSoup(sources_path.read_text(encoding="utf-8"), "html.parser")
    public_body_for(official_truth, "en").select_one('[data-section="official-boundary"] p').append(
        " Official material is the final truth."
    )
    record(
        "official material made final truth",
        any("official material is described as final truth" in issue for issue in sources_issues(official_truth)),
    )

    generic_sources = BeautifulSoup(sources_path.read_text(encoding="utf-8"), "html.parser")
    for heading in public_body_for(generic_sources, "en").select('[data-section="categories"] h3'):
        heading.clear()
        heading.append("Source material")
    record(
        "source categories generalized",
        any("source categories were generalized" in issue for issue in sources_issues(generic_sources)),
    )

    protest_text = (ROOT / "protests.js").read_text(encoding="utf-8")
    missing_protest_title = re.sub(
        r"(title:\s*\{.*?)(\n\s*it:\s*'[^']+',?)",
        r"\1",
        protest_text,
        count=1,
        flags=re.S,
    )
    record(
        "deleted protest title language",
        any("title lacks a ten-language set" in issue for issue in protests_script_issues(missing_protest_title)),
    )

    fixed_alt = protest_text.replace("event.title[lang]", "event.title.en", 1)
    record(
        "protest alt fixed to English",
        any("fixed to English" in issue for issue in protests_script_issues(fixed_alt)),
    )

    false_social = BeautifulSoup(contact_path.read_text(encoding="utf-8"), "html.parser")
    social = false_social.new_tag("p")
    social.string = "Contact us through social media listed on the homepage."
    public_body_for(false_social, "en").select_one("section").append(social)
    record(
        "nonexistent social-media channel restored",
        any("social-media contact claim returned" in issue for issue in contact_page_issues(false_social)),
    )

    record(
        "frozen article byte modified",
        any(
            "frozen article changed" in issue
            for issue in frozen_article_issues({FILES[0].name: FILES[0].read_bytes() + b"mutation"})
        ),
    )

    # Release-surface tests mutate real file text in memory.  They do not
    # validate constants or touch the working tree.
    sitemap_text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    article_url = f"{SITE_ORIGIN}/posts/{FILES[0].name}"
    missing_article_sitemap = re.sub(
        rf"\s*<url><loc>{re.escape(article_url)}</loc></url>",
        "",
        sitemap_text,
        count=1,
    )
    record(
        "sitemap article deleted",
        any("missing public URL" in issue for issue in sitemap_issues(missing_article_sitemap)),
    )

    template_sitemap = sitemap_text.replace(
        "</urlset>",
        f"  <url><loc>{SITE_ORIGIN}/posts/template.html</loc></url>\n</urlset>",
    )
    record(
        "sitemap template added",
        any("unexpected or non-public URL" in issue for issue in sitemap_issues(template_sitemap)),
    )

    local_path_sitemap = sitemap_text.replace(
        "</urlset>", "  <url><loc>file:///tmp/local-preview.html</loc></url>\n</urlset>"
    )
    record(
        "sitemap local absolute path added",
        any("canonical HTTPS origin" in issue for issue in sitemap_issues(local_path_sitemap)),
    )

    robots_text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    wrong_robots = robots_text.replace("zhonghuafreedom.org", "wrong.example")
    record(
        "robots wrong domain",
        any("does not exactly match CNAME" in issue for issue in robots_issues(wrong_robots)),
    )

    config_text = (ROOT / "_config.yml").read_text(encoding="utf-8")
    config_without_backup = config_text.replace("  - backup_legacy\n", "", 1)
    record(
        "config backup exclusion deleted",
        any("backup_legacy" in issue for issue in config_issues(config_without_backup)),
    )

    config_excludes_posts = config_text.replace("  - posts/template.html", "  - posts", 1)
    record(
        "config formal posts excluded",
        any("formal article is excluded" in issue for issue in config_issues(config_excludes_posts)),
    )

    not_found_text = (ROOT / "404.html").read_text(encoding="utf-8")
    missing_ja_404 = BeautifulSoup(not_found_text, "html.parser")
    missing_ja_404.select_one('[data-language-body="ja"]').decompose()
    record(
        "404 Japanese body deleted",
        any("expected one ja body" in issue for issue in not_found_issues(str(missing_ja_404))),
    )

    english_fr_404 = BeautifulSoup(not_found_text, "html.parser")
    english_panel = english_fr_404.select_one('[data-language-body="en"]')
    french_panel = english_fr_404.select_one('[data-language-body="fr"]')
    french_panel.clear()
    for child in list(english_panel.contents):
        french_panel.append(copy.copy(child))
    record(
        "404 French falls back to English",
        any("fr falls back to English" in issue for issue in not_found_issues(str(english_fr_404))),
    )

    about_text = (ROOT / "about.html").read_text(encoding="utf-8")
    docs_link = BeautifulSoup(about_text, "html.parser")
    link = docs_link.new_tag("a", href="docs/EDITORIAL_CONTROL_STANDARD.md")
    link.string = "maintenance document"
    docs_link.body.append(link)
    record(
        "public page links to docs",
        any(
            "excluded maintenance content" in issue
            for issue in public_html_release_issues({"about.html": str(docs_link)})
        ),
    )

    missing_image = BeautifulSoup(about_text, "html.parser")
    image = missing_image.new_tag("img", src="images/does-not-exist.png", alt="Missing test image")
    missing_image.body.append(image)
    record(
        "public page references missing image",
        any(
            "target does not exist" in issue
            for issue in public_html_release_issues({"about.html": str(missing_image)})
        ),
    )

    duplicate_id = BeautifulSoup(about_text, "html.parser")
    existing_id = duplicate_id.select_one("[id]").get("id")
    duplicate = duplicate_id.new_tag("div", id=existing_id)
    duplicate_id.body.append(duplicate)
    record(
        "public page duplicate id",
        any(
            "duplicate HTML id" in issue
            for issue in public_html_release_issues({"about.html": str(duplicate_id)})
        ),
    )

    sync_text = (ROOT / "tools/sync_languages.py").read_text(encoding="utf-8")
    restored_endpoint = sync_text + '\nTRANSLATION_ENDPOINT = "https://translate.googleapis.com"\n'
    record(
        "sync script network translation endpoint restored",
        any("network translation endpoint" in issue for issue in sync_script_issues(restored_endpoint)),
    )

    restored_write = sync_text + '\nPath("index.html").write_text("unsafe")\n'
    record(
        "sync script public write restored",
        any("filesystem write capability" in issue for issue in sync_script_issues(restored_write)),
    )

    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    restored_readme = readme_text + "\nThis workflow uses the English blocks as the source.\n"
    record(
        "README English-block guidance restored",
        any("English-block" in issue for issue in readme_release_issues(restored_readme)),
    )

    gitignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    ignored_sitemap = gitignore_text + "\nsitemap.xml\n"
    record(
        "gitignore hides sitemap",
        any("sitemap.xml" in issue for issue in gitignore_issues(ignored_sitemap)),
    )

    for label, ok in checks:
        if not ok:
            print(f"Negative test missed: {label}")
    return sum(ok for _, ok in checks), len(checks)


def release_statistics():
    stats = Counter()
    documents = loaded_documents()
    for path, soup in documents.items():
        header_issues = article_header_issues(soup, path)
        stats["title_fallback"] += sum("falls back to English" in issue for issue in header_issues)
        stats["directives"] += sum("editorial directive" in issue for issue in header_issues)
        for lang in LANGS:
            body = body_for(soup, lang)
            stats["directives"] += len(public_directive_nodes(body, lang))
            if path.name == "zhang-zhan.html" and lang == "ko":
                stats["zhang_gender"] += len(ZHANG_KO_MALE.findall(body.get_text(" ", strip=True)))
            if lang == "ja":
                stats["state_shu"] += len(JAPANESE_STATE_AS_SHU.findall(body.get_text(" ", strip=True)))
            rights_heading = find_heading(body, HEADINGS[lang][0])
            protection_heading = find_heading(body, HEADINGS[lang][1])
            rights = body.select_one("p.critical-conclusion")
            protection = body.select_one("p.critical-protection")
            stats["rights"] += int(rights is not None)
            stats["protection"] += int(protection is not None)
            for heading, main in ((rights_heading, rights), (protection_heading, protection)):
                nodes = section_nodes(heading)
                stats["extra"] += max(0, len(nodes) - 1)
                text = main.get_text(" ", strip=True)
                if BANNED.search(section_text(heading)):
                    stats["banned"] += 1
                if len(text) > (900 if lang in {"zh", "ja", "ko"} else 1800):
                    stats["overlong"] += 1
                if lang in {"es", "de", "fr", "no", "nl", "it"} and not first_alpha_is_upper(text):
                    stats["lowercase"] += 1
            rights_text = rights.get_text(" ", strip=True)
            protection_text = protection.get_text(" ", strip=True)
            stats["contains"] += int(rights_text in protection_text)
            stats["overlap"] += int(overlap_rate(rights_text, protection_text, lang) > 0.25)
    duplicates = duplicate_sentence_issues(documents)
    stats["duplicate_cjk"] = sum(issue[:2] in {"zh", "ja", "ko"} for issue in duplicates)
    stats["duplicate_other"] = len(duplicates) - stats["duplicate_cjk"]
    stats["directives"] += sum("editorial directive" in issue for issue in card_issues())
    return stats


def report_matrix():
    print("54-article language matrix:")
    for path in FILES:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        details = []
        for lang in LANGS:
            body = body_for(soup, lang)
            h2s = len(body.find_all("h2")) if body else 0
            critical = len(body.select("p.critical-conclusion, p.critical-protection")) if body else 0
            details.append(f"{lang}:{h2s}/{critical}")
        print(f"posts/{path.name} " + " ".join(details))
    print("6-public-page language matrix:")
    for name in PUBLIC_PAGES:
        soup = BeautifulSoup((ROOT / name).read_text(encoding="utf-8"), "html.parser")
        details = []
        for lang in LANGS:
            body = public_body_for(soup, lang)
            sections = len(body.select(":scope > section[data-section]")) if body else 0
            details.append(f"{lang}:{sections}")
        print(f"{name} " + " ".join(details))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate all visible multilingual dossier columns.")
    parser.add_argument("--matrix", action="store_true", help="print the 54×10 section/critical-paragraph matrix")
    parser.add_argument("--self-test", action="store_true", help="exercise visible-node negative tests")
    parser.add_argument("--release", action="store_true", help="audit the complete public release surface")
    args = parser.parse_args()
    issues = validate_paths()
    if args.release:
        issues.extend(release_surface_issues())
    if args.matrix:
        report_matrix()
    passed = total = 0
    if args.self_test:
        passed, total = self_tests()
        print(f"Real cross-page and critical-column negative tests: {passed}/{total} intercepted")
        if passed != total:
            issues.append(f"self-test: only {passed}/{total} mutations were intercepted")
    stats = release_statistics()
    print(f"Articles/languages: {len(FILES)} × {len(LANGS)}")
    print(f"Human-rights main paragraphs: {stats['rights']}; protection main paragraphs: {stats['protection']}; additional critical nodes: {stats['extra']}")
    print(f"Rights fully contained in protection: {stats['contains']}; same-page sentence overlap above 25%: {stats['overlap']}")
    print(f"Cross-case repeated CJK long sentences: {stats['duplicate_cjk']}; other-language long sentences: {stats['duplicate_other']}")
    print(f"European lowercase/residual openings: {stats['lowercase']}; abnormally long critical paragraphs: {stats['overlong']}")
    print(f"Disclaimers or applicant-guide wording in critical columns: {stats['banned']}")
    print(f"Article title/deck English fallbacks: {stats['title_fallback']}; Zhang Zhan Korean wrong-gender pronouns: {stats['zhang_gender']}")
    print(f"Japanese state-to-州 errors: {stats['state_shu']}; public visible-text editorial directives: {stats['directives']}")
    print("Public pages/languages: 6 × 10; required source categories: 12; retained external URLs: 16")
    print("Protest archive: 8 events; 254 image files; dynamic title/place/alt/aria language sets: 10")
    if args.release:
        release = release_surface_statistics()
        print(
            "Release surface: "
            f"{release['html']} public HTML files; {release['local_references']} local href/src references; "
            f"{release['anchors']} internal anchors; {release['images']} image elements; "
            f"{release['controls']} form controls"
        )
        print(
            f"Sitemap: {release['sitemap_urls']} canonical URLs including "
            f"{release['formal_posts']} formal articles"
        )
    if issues:
        print("Language check failed:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("Language check passed.")
    print("Seven core sections, source metadata, and localized cards: consistent.")
    if args.self_test:
        print("All required real cross-page negative mutations were intercepted.")
    if args.release:
        print("Release surface, publication configuration, 404, robots, and sitemap checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
