#!/usr/bin/env node
/**
 * Inject <figure class="article-cover"> into each posts/<slug>.html using
 * the metadata in posts/images/credits.json. Idempotent: re-running replaces
 * any previously-injected cover.
 */
const fs = require('fs');
const path = require('path');

const POSTS_DIR = path.join(__dirname, '..', 'posts');
const credits = JSON.parse(fs.readFileSync(path.join(POSTS_DIR, 'images', 'credits.json'), 'utf8'));

const COVER_RE = /\n\s*<figure class="article-cover">[\s\S]*?<\/figure>\n/;

for (const [slug, meta] of Object.entries(credits)) {
  const file = path.join(POSTS_DIR, slug + '.html');
  if (!fs.existsSync(file)) {
    console.log('SKIP (no html): ' + slug);
    continue;
  }
  let html = fs.readFileSync(file, 'utf8');

  // Strip any previous cover
  html = html.replace(COVER_RE, '\n');

  const artist = (meta.artist || 'Unknown').slice(0, 120);
  const license = meta.license || 'CC';
  const figure = `\n        <figure class="article-cover">\n            <img src="${meta.file}" alt="${escapeHtml(meta.title.replace(/^File:/, ''))}" loading="lazy">\n            <figcaption>\n                <span class="lang-zh">圖片：${escapeHtml(artist)} / ${escapeHtml(license)} · <a href="${meta.sourcePage}" target="_blank" rel="noopener">Wikimedia Commons</a></span>\n                <span class="lang-en">Image: ${escapeHtml(artist)} / ${escapeHtml(license)} · <a href="${meta.sourcePage}" target="_blank" rel="noopener">Wikimedia Commons</a></span>\n            </figcaption>\n        </figure>\n`;

  // Insert directly before <div class="container article-content">
  const marker = '<div class="container article-content">';
  if (html.indexOf(marker) === -1) {
    console.log('NO MARKER: ' + slug);
    continue;
  }
  html = html.replace(marker, figure + '        ' + marker);
  fs.writeFileSync(file, html);
  console.log('OK ' + slug);
}

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
