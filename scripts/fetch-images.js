#!/usr/bin/env node
/**
 * Search Wikimedia Commons via MediaWiki API for each article slug,
 * pick the first hit that has a usable (PD / CC) license, download it.
 */
const fs = require('fs');
const path = require('path');
const https = require('https');

const POSTS_DIR = path.join(__dirname, '..', 'posts');
const IMG_DIR = path.join(POSTS_DIR, 'images');
if (!fs.existsSync(IMG_DIR)) fs.mkdirSync(IMG_DIR, { recursive: true });

const QUERIES = {
  '2024-report': ['Universal Declaration of Human Rights document', 'United Nations Human Rights Council', 'Human rights protest'],
  '709-crackdown': ['Beijing Tianjin court building', 'Tianjin China court', 'Chinese police'],
  'ai-weiwei': ['Ai Weiwei portrait', 'Ai Weiwei artist', 'Ai Weiwei sunflower seeds'],
  'causeway-bay-books': ['Causeway Bay Books', 'Lam Wing-kee', 'Causeway Bay Hong Kong street'],
  'chen-guangcheng': ['Chen Guangcheng', 'blind activist Shandong'],
  'cultural-revolution': ['Cultural Revolution poster', 'Mao Zedong Red Guards', 'Cultural Revolution propaganda'],
  'dalai-lama-exile': ['14th Dalai Lama', 'Dalai Lama Tenzin Gyatso', 'Dharamsala Tibet'],
  'digital-surveillance': ['Surveillance camera street', 'Skynet camera China', 'CCTV camera city'],
  'falun-gong-persecution': ['Falun Gong protest', 'Falun Dafa exercise', 'Falun Gong meditation'],
  'feng-county-chained-woman': ['Xuzhou Jiangsu', 'Feng County Jiangsu', 'rural Jiangsu village'],
  'great-leap-famine': ['Great Leap Forward', 'Mao Zedong commune', 'backyard furnace China'],
  'hk-12': ['Hong Kong protest 2020', 'Hong Kong activists arrest', 'Hong Kong police protest'],
  'hk-47': ['Hong Kong primary election 2020', 'Joshua Wong activist', 'Hong Kong democracy primary'],
  'hong-kong-nsl': ['Hong Kong national security law', '2019 Hong Kong protests', 'Hong Kong umbrella movement'],
  'jiang-tianyong': ['Beijing court Tiananmen', 'Tiananmen Gate Beijing', 'Chinese supreme court building'],
  'land-reform-anti-rightist': ['Land Reform China 1950', 'Mao Zedong portrait', 'Anti-Rightist Movement China'],
  'li-wenliang': ['Wuhan China hospital', 'COVID-19 Wuhan 2020', 'Wuhan virus mask'],
  'liu-xia': ['Liu Xia poet', 'Liu Xiaobo wife', 'Liu Xiaobo'],
  'liu-xiaobo': ['Nobel Peace Prize empty chair 2010', 'Liu Xiaobo Nobel', 'Nobel Peace Prize ceremony'],
  'peng-zaizhou': ['Sitong Bridge Beijing', 'Beijing Haidian bridge', 'Beijing protest banner'],
  'shanghai-lockdown': ['Shanghai lockdown 2022', 'Shanghai COVID', 'Shanghai street COVID'],
  'tiananmen-1989': ['Tiananmen Square Beijing', 'Beijing 1989 protest', 'Tiananmen Square protests 1989'],
  'transnational-repression': ['China embassy', 'globe centered China', 'Chinese diaspora protest'],
  'wang-bingzhang': ['Statue of Liberty New York skyline', 'Statue of Liberty close up', 'Liberty Island'],
  'wang-quanzhang': ['China prison gate', 'Tianjin first intermediate court', 'Beijing Wangfujing'],
  'white-paper': ['blank A4 paper', 'White Paper Movement China', 'A4 paper white'],
  'xinjiang-camps': ['Xinjiang re-education camp', 'Uyghur Xinjiang', 'Xinjiang detention satellite'],
  'zhang-zhan': ['Wuhan street citizen journalist', 'Wuhan Hubei street', 'Wuhan COVID outbreak'],
};

const ALLOWED = /(public ?domain|cc[\s-]?by|cc[\s-]?0|cc[\s-]?sa|gfdl|fal|attribution|free)/i;
const FORBIDDEN = /(non[- ]?commercial|no derivative|fair use|copyrighted|all rights reserved)/i;

function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'zhonghuafreedom-image-fetcher/1.0 (https://zhonghuafreedom.org)' } }, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (c) => (body += c));
      res.on('end', () => resolve({ status: res.statusCode, body }));
    }).on('error', reject);
  });
}

function downloadBinary(url, dest, redirectsLeft = 6) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'zhonghuafreedom-image-fetcher/1.0 (https://zhonghuafreedom.org)' } }, (res) => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode)) {
        if (redirectsLeft <= 0) return reject(new Error('Too many redirects'));
        const next = new URL(res.headers.location, url).toString();
        res.resume();
        return resolve(downloadBinary(next, dest, redirectsLeft - 1));
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error('HTTP ' + res.statusCode));
      }
      const file = fs.createWriteStream(dest);
      res.pipe(file);
      file.on('finish', () => file.close(() => resolve()));
      file.on('error', reject);
    }).on('error', reject);
  });
}

const stripTags = (s) => String(s || '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();

async function searchCommons(query) {
  const u = 'https://commons.wikimedia.org/w/api.php?'
    + 'action=query&format=json&generator=search'
    + '&gsrsearch=' + encodeURIComponent(query)
    + '&gsrnamespace=6&gsrlimit=20'
    + '&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=1400';
  const { body } = await httpsGet(u);
  const data = JSON.parse(body);
  const pages = data?.query?.pages;
  if (!pages) return [];
  return Object.values(pages).map((p) => {
    const ii = (p.imageinfo && p.imageinfo[0]) || {};
    const meta = ii.extmetadata || {};
    return {
      title: p.title,
      thumburl: ii.thumburl,
      url: ii.url,
      mime: ii.mime,
      license: (meta.LicenseShortName && meta.LicenseShortName.value) || (meta.License && meta.License.value) || '',
      artist: stripTags((meta.Artist && meta.Artist.value) || ''),
      usageTerms: (meta.UsageTerms && meta.UsageTerms.value) || '',
      sourcePage: 'https://commons.wikimedia.org/wiki/' + encodeURIComponent(p.title.replace(/ /g, '_')),
    };
  });
}

function isUsable(item) {
  if (!item.url || !item.thumburl) return false;
  if (!/jpeg|jpg|png/i.test(item.mime || '')) return false;
  const lic = (item.license + ' ' + item.usageTerms).toLowerCase();
  if (FORBIDDEN.test(lic)) return false;
  return ALLOWED.test(lic);
}

(async () => {
  const credits = {};
  const missing = [];
  for (const [slug, queries] of Object.entries(QUERIES)) {
    let chosen = null;
    let trace = [];
    for (const q of queries) {
      try {
        const items = await searchCommons(q);
        const usable = items.filter(isUsable);
        trace.push(q + '=>' + usable.length + '/' + items.length);
        if (usable.length) { chosen = { item: usable[0], query: q }; break; }
      } catch (e) {
        trace.push(q + '=>ERR ' + e.message);
      }
    }
    if (!chosen) {
      console.log('[' + slug + '] NO RESULT  ' + trace.join(' | '));
      missing.push({ slug, trace });
      continue;
    }
    const ext = chosen.item.mime.includes('png') ? '.png' : '.jpg';
    const dest = path.join(IMG_DIR, slug + ext);
    try {
      await downloadBinary(chosen.item.thumburl, dest);
      credits[slug] = {
        file: 'images/' + slug + ext,
        title: chosen.item.title,
        artist: chosen.item.artist,
        license: chosen.item.license,
        sourcePage: chosen.item.sourcePage,
        query: chosen.query,
      };
      console.log('[' + slug + '] OK  ' + chosen.item.title + '  (' + chosen.item.license + ')');
    } catch (e) {
      console.log('[' + slug + '] DOWNLOAD FAIL ' + e.message);
      missing.push({ slug, error: e.message, candidate: chosen.item.title });
    }
  }
  fs.writeFileSync(path.join(IMG_DIR, 'credits.json'), JSON.stringify(credits, null, 2));
  fs.writeFileSync(path.join(IMG_DIR, 'missing.json'), JSON.stringify(missing, null, 2));
  console.log('\nDone. ' + Object.keys(credits).length + '/' + Object.keys(QUERIES).length);
  if (missing.length) console.log('Missing: ' + missing.map((m) => m.slug).join(', '));
})();
