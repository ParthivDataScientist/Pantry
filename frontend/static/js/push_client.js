/**
 * push_client.js — Browser Push Notification subscription.
 *
 * Registers the service worker and provides `subscribeToPush()` for
 * pantry staff to opt in to push notifications.
 *
 * Reads `token` from localStorage independently so this file has no hidden
 * dependency on variables defined in other scripts.
 */

// ── Service Worker registration ───────────────────────────────────────────────
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => {
        console.error('Service Worker registration failed:', err);
    });
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Convert a URL-safe base64 VAPID public key string to a Uint8Array,
 * as required by PushManager.subscribe().
 *
 * Handles keys that may include PEM headers, non-URL-safe characters,
 * or incorrect padding.
 *
 * @param {string} base64String - VAPID public key (URL-safe base64, no padding).
 * @returns {Uint8Array}
 */
function urlBase64ToUint8Array(base64String) {
    if (!base64String) {
        throw new Error('VAPID public key is missing or empty.');
    }

    const base64 = base64String
        .replace(/-----BEGIN PUBLIC KEY-----/g, '')
        .replace(/-----END PUBLIC KEY-----/g, '')
        .replace(/\s/g, '')        // remove whitespace / newlines
        .replace(/-/g, '+')        // URL-safe → standard base64
        .replace(/_/g, '/')
        .replace(/=/g, '');        // strip existing padding before recalculating

    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
    const rawData = window.atob(padded);

    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; i++) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Subscribe the current browser to push notifications and save the
 * subscription to the server.
 *
 * Reads the auth token from localStorage directly so this function can be
 * called from any page that loads this script.
 */
async function subscribeToPush() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Push notifications are not supported in this browser.');
        return;
    }

    // Read token independently — do not rely on a global from another script
    const token = localStorage.getItem('token');
    if (!token) {
        console.warn('Cannot subscribe to push: user is not authenticated.');
        return;
    }

    try {
        const registration = await navigator.serviceWorker.ready;

        const keyResponse = await fetch('/api/vapid-public-key');
        const { public_key: publicVapidKey } = await keyResponse.json();

        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicVapidKey),
        });

        await fetch('/api/subscribe', {
            method:  'POST',
            headers: {
                'Content-Type':  'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(subscription),
        });

        console.log('Push notification subscription saved successfully.');
    } catch (error) {
        console.error('Push subscription failed:', error);
    }
}
