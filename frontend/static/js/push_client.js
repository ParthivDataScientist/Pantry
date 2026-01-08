function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
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

        // Fetch public key from backend
        const response = await fetch('/api/vapid-public-key');
        if (!response.ok) {
            throw new Error('Failed to fetch VAPID public key');
        }
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
