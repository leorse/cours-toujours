const CACHE_NAME = 'parcours-v2';

const PRECACHE_URLS = [
  '/static/css/style.css',
  '/static/css/responsive.css',
  '/static/js/fraction_renderer.js',
  '/static/js/blueprint_renderer.js',
  '/static/js/touch_dragdrop.js',
  '/static/images/logo.png',
  '/static/images/soleil.png',
  '/static/images/lune.png',
  '/static/images/flash.png',
  '/static/images/gribouille_coucou.png',
  '/static/images/gribouille_doigt_leve.png',
  '/static/images/gribouille_info.png',
  '/static/images/gribouille_joie.png',
  '/static/images/gribouille_saute.png',
  '/manifest.json',
  // CDN resources
  'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css',
  'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js',
  'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js',
  'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
  'https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js',
];

// Install: precache all static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Activate: delete old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch strategy
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Never cache POST requests or auth/API routes
  if (request.method !== 'GET') return;
  if (['/login', '/logout', '/submit_step', '/submit_test_step', '/log_exercise'].some(p => url.pathname.startsWith(p))) return;

  // Cache-first for local static assets
  if (url.origin === self.location.origin && url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Cache-first for manifest
  if (url.origin === self.location.origin && url.pathname === '/manifest.json') {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Stale-while-revalidate for CDN resources
  if (url.hostname === 'cdn.jsdelivr.net' || url.hostname === 'fonts.gstatic.com' || url.hostname === 'fonts.googleapis.com') {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Network-first for HTML navigation
  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request));
    return;
  }
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, response.clone());
  }
  return response;
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || new Response('Hors ligne', { status: 503 });
  }
}

async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);
  const fetchPromise = fetch(request).then(response => {
    if (response.ok) {
      caches.open(CACHE_NAME).then(cache => cache.put(request, response.clone()));
    }
    return response;
  }).catch(() => null);
  return cached || await fetchPromise;
}
