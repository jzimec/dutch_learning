/* Dutch Learning update reliability: fetch app scripts from network first.
   Never cache account data or API responses. */
self.addEventListener('install', event => {
  event.waitUntil(self.skipWaiting());
});
self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});
self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.includes('/auth/') || url.pathname.includes('/rest/')) return;
  const isAppCode = req.mode === 'navigate' || /\.(?:js|css|html)$/.test(url.pathname) || url.pathname.endsWith('/dutch_learning/');
  if (!isAppCode) return;
  event.respondWith(fetch(new Request(req, {cache:'no-store'})).catch(() => caches.match(req).then(cached => cached || Response.error())));
});
