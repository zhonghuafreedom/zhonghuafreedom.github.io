const protestEvents = [
  {
    date: '2025-09-03',
    slug: '2025-09-03',
    count: 2,
    title: {
      zh: '反對歷史洗白與勝利敘事抗議',
      en: 'Reject Historical Whitewashing and Victory Narratives Protest',
      ja: '歴史の美化と勝利叙事に反対する抗議',
      ko: '역사 미화와 승리 서사에 반대하는 항의',
      es: 'Protesta contra el blanqueamiento histórico y los relatos de victoria',
      de: 'Protest gegen historische Beschönigung und Siegesnarrative',
      fr: 'Manifestation contre le blanchiment historique et les récits de victoire',
      no: 'Protest mot historievasking og seiersfortellinger',
      nl: 'Protest tegen historische witwassing en overwinningsverhalen',
      it: 'Protesta contro la riscrittura storica e le narrazioni di vittoria'
    },
    place: {
      zh: '地點未列明',
      en: 'Location not specified',
      ja: '場所未記載',
      ko: '장소 미기재',
      es: 'Lugar no especificado',
      de: 'Ort nicht angegeben',
      fr: 'Lieu non précisé',
      no: 'Sted ikke oppgitt',
      nl: 'Locatie niet vermeld',
      it: 'Luogo non specificato'
    }
  },
  {
    date: '2025-06-03',
    slug: '2025-06-03',
    count: 41,
    title: {
      zh: '紀念六四天安門屠殺抗議與遊行',
      en: 'March and Protest Commemorating the June 4, 1989 Tiananmen Massacre',
      ja: '六四天安門事件追悼デモと行進',
      ko: '6월 4일 천안문 학살 추모 행진과 항의',
      es: 'Marcha y protesta en memoria de la masacre de Tiananmén del 4 de junio',
      de: 'Marsch und Protest zum Gedenken an das Tiananmen-Massaker vom 4. Juni',
      fr: 'Marche et manifestation en mémoire du massacre de Tiananmen du 4 juin',
      no: 'Marsj og protest til minne om Tiananmen-massakren 4. juni',
      nl: 'Mars en protest ter herdenking van het Tiananmen-bloedbad van 4 juni',
      it: 'Marcia e protesta in memoria del massacro di Tiananmen del 4 giugno'
    },
    place: {
      zh: '紐約市，Greeley Square 至中國駐紐約總領事館',
      en: 'New York City, Greeley Square to the PRC Consulate',
      ja: 'ニューヨーク市、グリーリー・スクエアから中国総領事館へ',
      ko: '뉴욕시, 그릴리 스퀘어에서 중국 총영사관까지',
      es: 'Nueva York, de Greeley Square al Consulado de la RPC',
      de: 'New York City, vom Greeley Square zum Konsulat der VR China',
      fr: 'New York, de Greeley Square au consulat de la RPC',
      no: 'New York City, fra Greeley Square til Kinas konsulat',
      nl: 'New York City, van Greeley Square naar het Chinese consulaat',
      it: 'New York, da Greeley Square al consolato della RPC'
    }
  },
  {
    date: '2025-05-31',
    slug: '2025-05-31',
    count: 76,
    title: {
      zh: '中國大使館前譴責六四天安門屠殺抗議',
      en: 'Protest at the PRC Embassy Condemning the June 4 Tiananmen Massacre',
      ja: '中国大使館前で六四天安門事件を非難する抗議',
      ko: '중국 대사관 앞 6월 4일 천안문 학살 규탄 항의',
      es: 'Protesta ante la embajada de la RPC contra la masacre de Tiananmén',
      de: 'Protest vor der Botschaft der VR China gegen das Tiananmen-Massaker',
      fr: 'Manifestation devant l’ambassade de Chine contre le massacre de Tiananmen',
      no: 'Protest ved Kinas ambassade mot Tiananmen-massakren',
      nl: 'Protest bij de Chinese ambassade tegen het Tiananmen-bloedbad',
      it: 'Protesta davanti all’ambasciata cinese contro il massacro di Tiananmen'
    },
    place: {
      zh: '華盛頓特區，中國駐美國大使館',
      en: 'Washington, D.C., PRC Embassy',
      ja: 'ワシントンD.C.、中国大使館',
      ko: '워싱턴 D.C., 중국 대사관',
      es: 'Washington D. C., embajada de la RPC',
      de: 'Washington, D.C., Botschaft der VR China',
      fr: 'Washington, ambassade de la RPC',
      no: 'Washington, D.C., Kinas ambassade',
      nl: 'Washington D.C., Chinese ambassade',
      it: 'Washington, D.C., ambasciata della RPC'
    }
  },
  {
    date: '2024-06-04',
    slug: '2024-06-04',
    count: 48,
    title: {
      zh: '紀念六四天安門屠殺抗議與遊行',
      en: 'March and Protest Commemorating the June 4, 1989 Tiananmen Massacre',
      ja: '六四天安門事件追悼デモと行進',
      ko: '6월 4일 천안문 학살 추모 행진과 항의',
      es: 'Marcha y protesta en memoria de la masacre de Tiananmén del 4 de junio',
      de: 'Marsch und Protest zum Gedenken an das Tiananmen-Massaker vom 4. Juni',
      fr: 'Marche et manifestation en mémoire du massacre de Tiananmen du 4 juin',
      no: 'Marsj og protest til minne om Tiananmen-massakren 4. juni',
      nl: 'Mars en protest ter herdenking van het Tiananmen-bloedbad van 4 juni',
      it: 'Marcia e protesta in memoria del massacro di Tiananmen del 4 giugno'
    },
    place: {
      zh: '紐約市，Greeley Square 至中國駐紐約總領事館',
      en: 'New York City, Greeley Square to the PRC Consulate',
      ja: 'ニューヨーク市、グリーリー・スクエアから中国総領事館へ',
      ko: '뉴욕시, 그릴리 스퀘어에서 중국 총영사관까지',
      es: 'Nueva York, de Greeley Square al Consulado de la RPC',
      de: 'New York City, vom Greeley Square zum Konsulat der VR China',
      fr: 'New York, de Greeley Square au consulat de la RPC',
      no: 'New York City, fra Greeley Square til Kinas konsulat',
      nl: 'New York City, van Greeley Square naar het Chinese consulaat',
      it: 'New York, da Greeley Square al consolato della RPC'
    }
  },
  {
    date: '2024-05-16',
    slug: '2024-05-16',
    count: 16,
    title: {
      zh: '紐約時代廣場反共抗議',
      en: 'New York City Times Square Protest Against the Chinese Communist Party',
      ja: 'ニューヨーク・タイムズスクエア反中国共産党抗議',
      ko: '뉴욕 타임스스퀘어 중국 공산당 반대 항의',
      es: 'Protesta contra el Partido Comunista Chino en Times Square',
      de: 'Protest gegen die Kommunistische Partei Chinas am Times Square',
      fr: 'Manifestation contre le Parti communiste chinois à Times Square',
      no: 'Protest mot Kinas kommunistparti på Times Square',
      nl: 'Protest tegen de Chinese Communistische Partij op Times Square',
      it: 'Protesta contro il Partito Comunista Cinese a Times Square'
    },
    place: {
      zh: '紐約市，時代廣場',
      en: 'New York City, Times Square',
      ja: 'ニューヨーク市、タイムズスクエア',
      ko: '뉴욕시, 타임스스퀘어',
      es: 'Nueva York, Times Square',
      de: 'New York City, Times Square',
      fr: 'New York, Times Square',
      no: 'New York City, Times Square',
      nl: 'New York City, Times Square',
      it: 'New York, Times Square'
    }
  },
  {
    date: '2024-04-27',
    slug: '2024-04-27',
    count: 18,
    title: {
      zh: '紐約時代廣場反共抗議',
      en: 'New York City Times Square Protest Against the Chinese Communist Party',
      ja: 'ニューヨーク・タイムズスクエア反中国共産党抗議',
      ko: '뉴욕 타임스스퀘어 중국 공산당 반대 항의',
      es: 'Protesta contra el Partido Comunista Chino en Times Square',
      de: 'Protest gegen die Kommunistische Partei Chinas am Times Square',
      fr: 'Manifestation contre le Parti communiste chinois à Times Square',
      no: 'Protest mot Kinas kommunistparti på Times Square',
      nl: 'Protest tegen de Chinese Communistische Partij op Times Square',
      it: 'Protesta contro il Partito Comunista Cinese a Times Square'
    },
    place: {
      zh: '紐約市，時代廣場',
      en: 'New York City, Times Square',
      ja: 'ニューヨーク市、タイムズスクエア',
      ko: '뉴욕시, 타임스스퀘어',
      es: 'Nueva York, Times Square',
      de: 'New York City, Times Square',
      fr: 'New York, Times Square',
      no: 'New York City, Times Square',
      nl: 'New York City, Times Square',
      it: 'New York, Times Square'
    }
  },
  {
    date: '2023-12-30',
    slug: '2023-12-30',
    count: 12,
    title: {
      zh: '紐約時代廣場反共抗議',
      en: 'New York City Times Square Protest Against the Chinese Communist Party',
      ja: 'ニューヨーク・タイムズスクエア反中国共産党抗議',
      ko: '뉴욕 타임스스퀘어 중국 공산당 반대 항의',
      es: 'Protesta contra el Partido Comunista Chino en Times Square',
      de: 'Protest gegen die Kommunistische Partei Chinas am Times Square',
      fr: 'Manifestation contre le Parti communiste chinois à Times Square',
      no: 'Protest mot Kinas kommunistparti på Times Square',
      nl: 'Protest tegen de Chinese Communistische Partij op Times Square',
      it: 'Protesta contro il Partito Comunista Cinese a Times Square'
    },
    place: {
      zh: '紐約市，時代廣場',
      en: 'New York City, Times Square',
      ja: 'ニューヨーク市、タイムズスクエア',
      ko: '뉴욕시, 타임스스퀘어',
      es: 'Nueva York, Times Square',
      de: 'New York City, Times Square',
      fr: 'New York, Times Square',
      no: 'New York City, Times Square',
      nl: 'New York City, Times Square',
      it: 'New York, Times Square'
    }
  },
  {
    date: '2023-12-16',
    slug: '2023-12-16',
    count: 41,
    title: {
      zh: '紐約時代廣場反共抗議',
      en: 'New York City Times Square Protest Against the Chinese Communist Party',
      ja: 'ニューヨーク・タイムズスクエア反中国共産党抗議',
      ko: '뉴욕 타임스스퀘어 중국 공산당 반대 항의',
      es: 'Protesta contra el Partido Comunista Chino en Times Square',
      de: 'Protest gegen die Kommunistische Partei Chinas am Times Square',
      fr: 'Manifestation contre le Parti communiste chinois à Times Square',
      no: 'Protest mot Kinas kommunistparti på Times Square',
      nl: 'Protest tegen de Chinese Communistische Partij op Times Square',
      it: 'Protesta contro il Partito Comunista Cinese a Times Square'
    },
    place: {
      zh: '紐約市，時代廣場',
      en: 'New York City, Times Square',
      ja: 'ニューヨーク市、タイムズスクエア',
      ko: '뉴욕시, 타임스스퀘어',
      es: 'Nueva York, Times Square',
      de: 'New York City, Times Square',
      fr: 'New York, Times Square',
      no: 'New York City, Times Square',
      nl: 'New York City, Times Square',
      it: 'New York, Times Square'
    }
  }
];

const galleryLabels = {
  photos: { zh: '張照片', en: 'photos', ja: '枚の写真', ko: '장 사진', es: 'fotos', de: 'Fotos', fr: 'photos', no: 'bilder', nl: 'foto’s', it: 'foto' },
  open: { zh: '打開照片', en: 'Open photo', ja: '写真を開く', ko: '사진 열기', es: 'Abrir foto', de: 'Foto öffnen', fr: 'Ouvrir la photo', no: 'Åpne bilde', nl: 'Foto openen', it: 'Apri foto' },
  total: {
    zh: '8 場活動 · 254 張照片',
    en: '8 events · 254 photos',
    ja: '8件の活動 · 254枚の写真',
    ko: '8개 활동 · 254장 사진',
    es: '8 eventos · 254 fotos',
    de: '8 Veranstaltungen · 254 Fotos',
    fr: '8 événements · 254 photos',
    no: '8 arrangementer · 254 bilder',
    nl: '8 activiteiten · 254 foto’s',
    it: '8 eventi · 254 foto'
  }
};

function langSpans(values) {
  return Object.entries(values).map(([lang, text]) => `<span class="lang-${lang}">${text}</span>`).join('');
}

function padPhotoNumber(index) {
  return String(index).padStart(3, '0');
}

document.addEventListener('DOMContentLoaded', () => {
  const gallery = document.querySelector('[data-protest-gallery]');
  const summary = document.querySelector('[data-protest-summary]');
  if (!gallery || !summary) return;

  summary.innerHTML = langSpans(galleryLabels.total);

  gallery.innerHTML = protestEvents.map((event) => {
    const photos = Array.from({ length: event.count }, (_, index) => {
      const number = padPhotoNumber(index + 1);
      const src = `images/protests/${event.slug}/photo-${number}.jpg`;
      return `
        <a class="protest-photo" href="${src}" target="_blank" rel="noopener noreferrer" aria-label="${event.date} ${galleryLabels.open.en} ${number}">
          <img src="${src}" alt="${event.date} ${event.title.en} photo ${number}" loading="lazy">
        </a>`;
    }).join('');

    return `
      <section class="protest-event" id="event-${event.slug}">
        <div class="protest-event-header">
          <div>
            <span class="protest-date">${event.date}</span>
            <h2>${langSpans(event.title)}</h2>
            <p class="protest-place">${langSpans(event.place)}</p>
          </div>
          <div class="protest-count"><strong>${event.count}</strong><span>${langSpans(galleryLabels.photos)}</span></div>
        </div>
        <div class="protest-photo-grid">${photos}</div>
      </section>`;
  }).join('');
});
