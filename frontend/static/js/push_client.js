function urlBase64ToUint8Array(base64String) {
    if (!base64String) {
        throw new Error("Invalid VAPID key: Key is empty");
    }

    // Clean the string: remove PEM headers/footers, newlines/whitespace, and existing padding
    const base64 = base64String
        .replace(/-----BEGIN PUBLIC KEY-----/g, '')
        .replace(/-----END PUBLIC KEY-----/g, '')
        .replace(/\s/g, '')
        .replace(/-/g, '+')
        .replace(/_/g, '/')
        .replace(/=/g, ''); // Remove existing padding to recalculate perfectly

    // Add padding if needed
    const padding = '='.repeat((4 - base64.length % 4) % 4);
    const base64Padded = base64 + padding;

    const rawData = window.atob(base64Padded);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Global function to trigger subscription
async function subscribeToPush() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        alert("Push notifications are not supported in this browser.");
        return;
    }

    try {
        const registration = await navigator.serviceWorker.ready;

        // Fetch public key from server
        const response = await fetch('/api/vapid-public-key');
        const data = await response.json();
        const publicVapidKey = data.public_key;

        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
        });

        console.log("Subscribed:", subscription);

        // Send to backend
        await fetch('/api/subscribe', {
            method: 'POST',
            body: JSON.stringify(subscription),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        alert("Subscribed to notifications!");

    } catch (error) {
        console.error("Subscription failed:", error);
        alert("Could not subscribe: " + error.message);
    }
}

// Register SW
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(function (registration) {
            console.log('Service Worker Registered');
        });
}
