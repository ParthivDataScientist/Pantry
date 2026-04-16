/**
 * pantry.js â€” Kitchen Display Screen.
 *
 * Polls /api/pantry/orders every 5 seconds, renders order cards,
 * plays an audio bell for new orders, and announces them via speech synthesis.
 * Requires "START NOW" to be clicked first to unblock browser audio policy.
 */

// â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
/** Retrieve token from localStorage OR from browser cookies */
function getAuthToken() {
    // Try localStorage first
    const lToken = localStorage.getItem('token');
    if (lToken) return lToken;

    // Fallback: look in document.cookie (token=xxxxx;)
    const name = 'token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i].trim();
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return null;
}

// â”€â”€ Auth guard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const token = getAuthToken();
if (!token) {
    window.location.href = '/';
}

// â”€â”€ State â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
/** IDs of orders visible at the last poll cycle. */
let lastKnownOrderIds = new Set();
/** IDs of orders that have already triggered the "late order" alert. */
let alertedLateOrderIds = new Set();
/** Set to true after the first successful poll, so we don't alert on load. */
let isInitialLoad = true;

/** @type {AudioContext|null} */
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

// â”€â”€ Audio â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function initAudio() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
}

/**
 * Play a synthesised bell chord using the Web Audio API.
 * Uses A5 major harmonics for a pleasant kitchen-bell feel.
 */
function playBellSound() {
    try {
        initAudio();
        const now = audioContext.currentTime;
        const masterGain = audioContext.createGain();
        masterGain.gain.setValueAtTime(0.5, now);
        masterGain.gain.exponentialRampToValueAtTime(0.01, now + 1.5);
        masterGain.connect(audioContext.destination);

        const harmonics = [880, 1109, 1318, 1760]; // A5 major chord
        harmonics.forEach((freq, i) => {
            const osc = audioContext.createOscillator();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now);

            const gain = audioContext.createGain();
            gain.gain.setValueAtTime(0.1 / (i + 1), now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + (1.5 - i * 0.2));

            osc.connect(gain);
            gain.connect(masterGain);

            osc.start(now);
            osc.stop(now + 2);
        });
    } catch (e) {
        console.error('Bell sound failed:', e);
    }
}

// â”€â”€ Speech synthesis â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

/**
 * Select the best available voice, prioritizing high-quality Hindi or Indian English.
 */
function getBestVoice() {
    const voices = window.speechSynthesis.getVoices();
    
    // Priority 1: Hindi (hi-IN) - specifically for the Hindi text used in item names
    const hindiVoice = voices.find(v => v.lang === 'hi-IN');
    if (hindiVoice) return hindiVoice;

    // Priority 2: Indian English (en-IN) - often sounds more natural with Hindi-mixed sentences
    const indianEnglishVoice = voices.find(v => v.lang === 'en-IN');
    if (indianEnglishVoice) return indianEnglishVoice;

    // Priority 3: Fallback to any voice with "India" in the name (e.g., Google's localized voices)
    const regionalVoice = voices.find(v => v.name.toLowerCase().includes('india'));
    if (regionalVoice) return regionalVoice;

    return voices[0] || null; // Final fallback to system default
}

/**
 * Speak *text* using the speech synthesis API.
 * @param {string} text - The text to read aloud.
 * @param {Function} [onEnd] - Optional callback invoked when speech ends.
 */
function speak(text, onEnd) {
    const utterance = new SpeechSynthesisUtterance(text);
    const voice = getBestVoice();
    
    if (voice) {
        utterance.voice = voice;
        // If it's a Hindi voice, the lang should match the voice
        utterance.lang = voice.lang; 
    }
    
    utterance.rate = 0.9;  // Slightly slower for better clarity in kitchen environments
    utterance.pitch = 1.0;
    if (onEnd) utterance.onend = onEnd;
    
    window.speechSynthesis.cancel(); // Stop any current speech before starting new one
    window.speechSynthesis.speak(utterance);
}

/**
 * Announce a new order aloud â€” spoken twice for clarity.
 * Uses the onend callback to chain the second utterance after the first
 * finishes, preventing cancellation issues.
 * @param {object} order - Order object from the API.
 */
function announceOrder(order) {
    try {
        const items = JSON.parse(order.items);
        const itemText = items
            .map(i => `${i.quantity} ${i.name_hindi || i.name}`)
            .join(', ');

        let text = `${order.employee_id} se naya order. ${itemText}.`;
        if (order.notes) {
            text += ` Note: ${order.notes}.`;
        }

        // Speak first time, then chain second announcement via onend
        speak(text, () => speak(text));
    } catch (e) {
        console.error('Speech announcement failed:', e);
    }
}

// â”€â”€ Kitchen session start â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

/**
 * Called when the user clicks "START NOW".
 * Unblocks the AudioContext and primes speech synthesis.
 */
function startKitchen() {
    initAudio();
    localStorage.setItem('kitchen_started', 'true'); // Persist "started" state
    document.getElementById('start-overlay').style.display = 'none';
    speak('Kitchen system ready. Voice notifications enabled.');
}

// Check if kitchen was previously started to auto-hide overlay
window.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('kitchen_started') === 'true') {
        console.log('[Init] Kitchen previously started. Auto-hiding overlay.');
        document.getElementById('start-overlay').style.display = 'none';
        
        // Note: Browsers will likely still block audio until the FIRST user interaction 
        // on the new page. But at least the dashboard is visible immediately.
        // We'll try to resume audio context if possible.
        initAudio();
    }
});

// Tap anywhere on the overlay to start (in case the button is missed)
document.addEventListener('click', () => {
    const overlay = document.getElementById('start-overlay');
    if (overlay && overlay.style.display !== 'none') {
        startKitchen();
    }
}, { once: true });

// This ensures the voice list is populated as soon as the browser has them ready
window.speechSynthesis.onvoiceschanged = () => {
    console.log("Voices updated:", window.speechSynthesis.getVoices().length);
    getBestVoice(); 
};

// â”€â”€ Clock â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function updateClock() {
    document.getElementById('clock').textContent = new Date().toLocaleTimeString();
}
setInterval(updateClock, 1000);

// â”€â”€ Order polling â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

/** Counter for consecutive authentication failures */
let authFailCount = 0;

async function fetchOrders() {
    try {
        const response = await fetch('/api/pantry/orders', {
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.status === 401) {
            authFailCount++;
            console.error(`Auth failure #${authFailCount}`);
            
            // On TV browsers, we want to be extra careful before logging out.
            // If it's a transient server issue, we don't want to kick the user.
            // If it fails 3 times in a row, then we redirect.
            if (authFailCount >= 3) {
                localStorage.removeItem('token');
                document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
                window.location.href = '/';
                return;
            }
            
            // Don't process this failed request, wait for next poll
            return;
        }

        // Success: reset failure counter
        authFailCount = 0;

        const orders = await response.json();
        processNewOrders(orders);
        processLateOrders(orders);

        lastKnownOrderIds = new Set(orders.map(o => o.id));
        isInitialLoad = false;

        renderOrders(orders);
    } catch (e) {
        console.warn('Network error or server down, retrying:', e);
        // Silently ignore transient network errors â€” the next poll will retry
    }
}

/**
 * Detect orders that weren't present in the last poll and trigger alerts.
 * @param {object[]} orders
 */
function processNewOrders(orders) {
    if (isInitialLoad) return; // Don't alert for orders that exist on page load

    const newOrders = orders.filter(o => !lastKnownOrderIds.has(o.id));
    if (newOrders.length > 0) {
        playBellSound();
        ensureScreenWakeLock('new-order');
        newOrders.forEach(o => announceOrder(o));
    }
}

/**
 * Alert for orders that have been pending for more than 5 minutes.
 * @param {object[]} orders
 */
function processLateOrders(orders) {
    const LATE_THRESHOLD_MS = 5 * 60 * 1000; // 5 minutes
    const now = Date.now();

    orders.forEach(order => {
        if (!order.timestamp) return;
        const ageMs = now - new Date(order.timestamp).getTime();

        if (ageMs > LATE_THRESHOLD_MS && !alertedLateOrderIds.has(order.id)) {
            playBellSound();
            alertedLateOrderIds.add(order.id);
        }
    });
}

// â”€â”€ Rendering â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function renderOrders(orders) {
    const container = document.getElementById('orders-container');
    container.innerHTML = '';

    if (orders.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-gray-500 mt-20 text-xl">NO PENDING ORDERS</div>';
        return;
    }

    orders.forEach(order => {
        container.appendChild(buildOrderCard(order));
    });
}

/**
 * Build a single order card DOM element.
 * @param {object} order - Order from the API.
 * @returns {HTMLElement}
 */
function buildOrderCard(order) {
    const items = JSON.parse(order.items);
    const card  = document.createElement('div');
    card.className = 'bg-white text-gray-900 rounded-lg p-4 shadow-lg card-enter flex flex-col justify-between min-h-[250px] border-l-8 border-yellow-500';

    const itemsHtml = items.map(item => `
        <li class="flex justify-between items-center text-lg border-b border-gray-100 last:border-0 py-2">
            <div class="flex items-center">
                ${item.image_url ? `<img src="${item.image_url}" class="w-12 h-12 rounded object-cover mr-3 border border-gray-200" alt="">` : ''}
                <div class="flex flex-col">
                    <span class="font-bold text-gray-800">${item.name_hindi || item.name}</span>
                    ${item.name_hindi ? `<span class="text-xs text-gray-400">${item.name}</span>` : ''}
                </div>
            </div>
            <span class="font-bold bg-gray-200 px-2 rounded">x${item.quantity}</span>
        </li>
    `).join('');

    const notesHtml = order.notes
        ? `<div class="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
               <strong>Note:</strong> ${order.notes}
           </div>`
        : '';

    card.innerHTML = `
        <div>
            <div class="flex justify-between items-start mb-4 border-b pb-2">
                <div>
                    <h3 class="font-bold text-lg text-gray-500 mb-1">Order #${order.id}</h3>
                    <p class="text-3xl font-black text-gray-900 uppercase tracking-wide mb-2">${order.employee_id}</p>
                </div>
            </div>
            <ul class="space-y-2 mb-4">${itemsHtml}</ul>
            ${notesHtml}
        </div>
        <button onclick="markOrderDone(${order.id})"
            class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded text-lg uppercase transition">
            Ready
        </button>
    `;

    return card;
}

// â”€â”€ Mark done â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

async function markOrderDone(orderId) {
    try {
        const response = await fetch(`/api/order/${orderId}/done`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (!response.ok) {
            console.error(`Failed to mark order #${orderId} as done (${response.status})`);
            return;
        }

        fetchOrders(); // Refresh the display
    } catch (e) {
        console.error(`Network error marking order #${orderId} as done:`, e);
    }
}

function startFallbackKeepAlive() {
    setInterval(() => {
        window.scrollBy(0, 1);
        window.scrollBy(0, -1);
    }, 2 * 60 * 1000);
}

setupWakeLockHandlers();

if (!('wakeLock' in navigator)) {
    startFallbackKeepAlive();
}

// Poll every 5 seconds
setInterval(fetchOrders, ORDER_POLL_MS);
fetchOrders();

