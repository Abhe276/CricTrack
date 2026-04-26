// app.js registers the service worker and handles the install and activate events to manage caching of static assets for offline use.

if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker
        .register("/static/serviceworker.js")
        .then(function(registration) {
            console.log("ServiceWorker registered:", registration);
        })
        .catch(function(error) {
            console.log("ServiceWorker registration failed:", error);
        }); 
    });
}
