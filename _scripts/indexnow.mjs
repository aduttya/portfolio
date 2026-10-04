// IndexNow submission for aduttya.com (Bing, Yandex, Seznam, Naver; not Google).
// The key file lives at the repo root as <key>.txt and must be live before submitting.
//
//   node _scripts/indexnow.mjs                    # every URL in the live sitemap
//   node _scripts/indexnow.mjs /about/ /work/     # specific paths or full URLs
//   node _scripts/indexnow.mjs --dry              # print without sending

const KEY = 'd7467c71a10b399b5270648182802993';
const HOST = 'aduttya.com';
const ORIGIN = `https://${HOST}`;
const ENDPOINT = 'https://api.indexnow.org/indexnow';

const normalize = (u) => (u.startsWith('http') ? u : `${ORIGIN}${u.startsWith('/') ? '' : '/'}${u}`);

async function urlsFromSitemap() {
  const res = await fetch(`${ORIGIN}/sitemap.xml`);
  if (!res.ok) throw new Error(`Sitemap fetch failed: ${res.status}`);
  const xml = await res.text();
  return [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim());
}

const args = process.argv.slice(2);
const dry = args.includes('--dry');
const explicit = args.filter((a) => !a.startsWith('--')).map(normalize);
const urls = explicit.length ? explicit : await urlsFromSitemap();

console.log(`Submitting ${urls.length} URL(s) to IndexNow${dry ? ' (dry run)' : ''}`);
if (dry) {
  urls.forEach((u) => console.log(`  ${u}`));
  process.exit(0);
}

const res = await fetch(ENDPOINT, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json; charset=utf-8' },
  body: JSON.stringify({ host: HOST, key: KEY, keyLocation: `${ORIGIN}/${KEY}.txt`, urlList: urls }),
});
// 200 accepted, 202 accepted pending key validation, 403 key not found, 422 bad URLs, 429 throttled
console.log(`HTTP ${res.status} ${res.statusText}`);
if (res.status >= 400) {
  console.error(await res.text());
  process.exit(1);
}
