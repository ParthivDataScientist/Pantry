
let lastKnownOrderIds = new Set();
let audioContext = null;
let wakeLockSentinel = null;
let wakeLockRetryTimer = null;
let wakeLockUnsupportedLogged = false;

const ORDER_POLL_MS = 5000;
const WAKE_LOCK_RETRY_MS = 15000;
const WAKE_LOCK_HEARTBEAT_MS = 30000;

function updateWakeLockStatus(message, isError = false) {
    const statusEl = document.getElementById('wake-lock-status');
    if (!statusEl) return;

    statusEl.textContent = `Screen Awake: ${message}`;
    statusEl.classList.toggle('border-red-500', isError);
    statusEl.classList.toggle('text-red-300', isError);
    statusEl.classList.toggle('border-gray-600', !isError);
    statusEl.classList.toggle('text-gray-300', !isError);
}

function scheduleWakeLockRetry() {
    if (wakeLockRetryTimer) return;
    wakeLockRetryTimer = setTimeout(() => {
        wakeLockRetryTimer = null;
        ensureScreenWakeLock('retry');
    }, WAKE_LOCK_RETRY_MS);
}

async function ensureScreenWakeLock(reason = 'background') {
    if (!('wakeLock' in navigator)) {
        if (!wakeLockUnsupportedLogged) {
            wakeLockUnsupportedLogged = true;
            updateWakeLockStatus('Unsupported');
            console.warn('Screen Wake Lock API is not supported on this browser.');
        }
        return false;
    }

    if (document.visibilityState !== 'visible') {
        updateWakeLockStatus('Paused');
        return false;
    }

    if (wakeLockSentinel && !wakeLockSentinel.released) {
        updateWakeLockStatus('Active');
        return true;
    }

    try {
        wakeLockSentinel = await navigator.wakeLock.request('screen');
        wakeLockSentinel.addEventListener('release', () => {
            wakeLockSentinel = null;
            updateWakeLockStatus('Released');
            scheduleWakeLockRetry();
        });
        updateWakeLockStatus('Active');
        console.log(`Wake lock acquired (${reason}).`);
        return true;
    } catch (error) {
        updateWakeLockStatus('Retrying', true);
        console.warn(`Wake lock request failed (${reason}).`, error);
        scheduleWakeLockRetry();
        return false;
    }
}

function setupWakeLockHandlers() {
    ensureScreenWakeLock('startup');

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            ensureScreenWakeLock('visibility');
            fetchOrders();
        } else {
            updateWakeLockStatus('Paused');
        }
    });

    ['click', 'touchstart', 'keydown'].forEach(eventName => {
        document.addEventListener(eventName, () => {
            ensureScreenWakeLock('interaction');
        }, { passive: true });
    });

    setInterval(() => {
        ensureScreenWakeLock('heartbeat');
    }, WAKE_LOCK_HEARTBEAT_MS);
}

function initAudio() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
    const soundBtn = document.getElementById('sound-toggle');
    if (soundBtn) {
        soundBtn.innerHTML = '🔔 Sound On';
        soundBtn.classList.remove('bg-red-500');
        soundBtn.classList.add('bg-green-500');
    }
}

// Audio context needs a user gesture to start in most browsers
document.addEventListener('click', initAudio, { once: true });

function playBellSound() {
    try {
        initAudio();

        const now = audioContext.currentTime;
        const gain = audioContext.createGain();

        // Bell sound: multiple oscillators for harmonics
        const frequencies = [880, 1109, 1318, 1760]; // A5 major chord harmonics

        frequencies.forEach((freq, i) => {
            const osc = audioContext.createOscillator();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now);

            // Slightly different decay for each harmonic
            const individualGain = audioContext.createGain();
            individualGain.gain.setValueAtTime(0.1 / (i + 1), now);
            individualGain.gain.exponentialRampToValueAtTime(0.001, now + (1.5 - (i * 0.2)));

            osc.connect(individualGain);
            individualGain.connect(gain);

            osc.start(now);
            osc.stop(now + 2);
        });

        gain.gain.setValueAtTime(0.5, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 1.5);

        gain.connect(audioContext.destination);

        console.log("Bell ring played!");
    } catch (e) {
        console.error("Audio play failed:", e);
    }
}

const token = localStorage.getItem('token');
if (!token) window.location.href = '/';

function updateClock() {
    document.getElementById('clock').innerText = new Date().toLocaleTimeString();
}
setInterval(updateClock, 1000);

async function fetchOrders() {
    try {
        const response = await fetch('/api/pantry/orders', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.status === 401) {
            window.location.href = '/';
            return;
        }
        const orders = await response.json();

        // Detect new orders for sound
        let hasNewOrder = false;
        const currentIds = new Set(orders.map(o => o.id));

        if (lastKnownOrderIds.size > 0) { // Don't ring on first load if orders already exist
            orders.forEach(o => {
                if (!lastKnownOrderIds.has(o.id)) {
                    hasNewOrder = true;
                }
            });
        }

        if (hasNewOrder) {
            playBellSound();
            ensureScreenWakeLock('new-order');
        }

        lastKnownOrderIds = currentIds;
        renderOrders(orders);
    } catch (e) {
        console.error("Failed to fetch orders");
    }
}

function renderOrders(orders) {
    const container = document.getElementById('orders-container');

    container.innerHTML = '';

    if (orders.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-gray-500 mt-20 text-xl">NO PENDING ORDERS</div>';
        return;
    }

    orders.forEach(order => {
        const items = JSON.parse(order.items);

        const card = document.createElement('div');
        card.className = 'bg-white text-gray-900 rounded-lg p-4 shadow-lg card-enter flex flex-col justify-between min-h-[250px] border-l-8 border-yellow-500';

        card.innerHTML = `
            <div>
                <div class="flex justify-between items-start mb-4 border-b pb-2">
                    <div>
                        <h3 class="font-bold text-lg text-gray-500 mb-1">Order #${order.id}</h3>
                        <p class="text-3xl font-black text-gray-900 uppercase tracking-wide mb-2">${order.employee_id}</p>
                    </div>
                </div>
                <ul class="space-y-2 mb-4">
                    ${items.map(i => `
                        <li class="flex justify-between items-center text-lg">
                            <span>${i.name}</span>
                            <span class="font-bold bg-gray-200 px-2 rounded">x${i.quantity}</span>
                        </li>
                    `).join('')}
                </ul>
                ${order.notes ? `
                    <div class="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
                        <strong>Note:</strong> ${order.notes}
                    </div>
                ` : ''}
            </div>
            <button onclick="markDone(${order.id})" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded text-lg uppercase transition">
                Ready
            </button>
        `;
        container.appendChild(card);
    });
}

async function markDone(id) {
    try {
        await fetch(`/api/order/${id}/done`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        fetchOrders();
    } catch (e) {
        console.error(e);
    }
}

setupWakeLockHandlers();

// Poll every 5 seconds
setInterval(fetchOrders, ORDER_POLL_MS);
fetchOrders();
