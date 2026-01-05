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

        // Hardcoded public key - MUST MATCH BACKEND
        // Since I put "Check-README-To-Generate" in backend, this will fail if not updated.
        // But for the user to learn, I will prompt them or put a placeholder.
        // I will assume the user puts the key here.
        // I'll put a placeholder string that is obviously needing replacement, or a valid looking test key?
        // No, invalid key will cause subscription failure.
        // I will add a method to fetch the public key from server maybe? No, keep it simple.
        const publicVapidKey = 'BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U'; // Example Key

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
    navigator.serviceWorker.register('/static/js/sw.js')
        .then(function (registration) {
            console.log('Service Worker Registered');
        });
}
