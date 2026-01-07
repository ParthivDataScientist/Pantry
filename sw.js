// frontend/static/js/sw.js

// This file handles background push events
self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : { title: 'New Order', body: 'Check the pantry!', url: '/pantry' };

    const options = {
        body: data.body,
        icon: '/static/img/icon.png',
        vibrate: [100, 50, 100],
        data: { url: data.url },
        requireInteraction: true // Keep notification until clicked/closed
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Open the app when the notification is clicked
self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(windowClients => {
            // Check if there is already a window/tab open with the target URL
            for (var i = 0; i < windowClients.length; i++) {
                var client = windowClients[i];
                // If so, just focus it.
                if (client.url.includes('pantry') && 'focus' in client) {
                    return client.focus();
                }
            }
            // If not, open a new window
            if (clients.openWindow) {
                return clients.openWindow(event.notification.data.url || '/pantry');
            }
        })
    );
});