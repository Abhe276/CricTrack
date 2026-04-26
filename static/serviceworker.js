// saves core assests so the app works offline 

const CACHE_NAME = "crictrack-v1";

const ASSETS = [
    "/",
    "/static/style.css",
    "/static/app.js",
    "/static/manifest.json",
    "/login",
    "/register",
];

// Install all the core asserts
self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            console.log("CricTrack: caching core assets");
            return cache.addAll(ASSETS);
        })
    );
});

// delete the OLD caches only, keep the present one

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                cacheNames
                    .filter(function (name) {
                        return name !== CACHE_NAME;
                    })
                    .map(function (name) {
                        console.log("CricTrack: deleting old cache", name);
                        return caches.delete(name);
                    })
            );
        })
    );
});


self.addEventListener("fetch", function (event) {
    event.respondWith(
        caches.match(event.request).then(function (cachedResponse) {
            if (cachedResponse) {
                return cachedResponse;
            }
            return fetch(event.request);
        })
    );
});

