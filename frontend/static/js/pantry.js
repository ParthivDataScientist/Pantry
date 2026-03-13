
let lastKnownOrderIds = new Set();
let alertedOrderIds = new Set();
let audioContext = null;
let isInitialized = false;

function initAudio() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
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

function speakOrder(order) {
    try {
        const items = JSON.parse(order.items);
        const itemStrings = items.map(i => `${i.quantity} ${i.name_hindi || i.name}`);
        const text = `New order from ${order.employee_id}. ${itemStrings.join(', ')}.`;
        
        console.log("Preparing to speak:", text);

        const speak = (content) => {
            const utterance = new SpeechSynthesisUtterance(content);
            const voices = window.speechSynthesis.getVoices();
            
            // Prioritize Indian English accent
            const indianVoice = voices.find(v => v.lang === 'en-IN' || v.lang === 'hi-IN') || 
                               voices.find(v => v.lang.includes('IN')) ||
                               voices.find(v => v.lang.startsWith('en-GB')) ||
                               voices[0];
            
            if (indianVoice) {
                utterance.voice = indianVoice;
                console.log("Using voice:", indianVoice.name);
            } else {
                console.warn("No suitable voice found, using default.");
            }
            
            utterance.rate = 0.85;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        };

        // Clear any existing speech
        window.speechSynthesis.cancel();
        
        // Speak twice with a small delay between them
        speak(text);
        setTimeout(() => speak(text), 100); // Small gap is usually enough for the queue
        
    } catch (e) {
        console.error("Speech synthesis failed:", e);
    }
}

function startKitchen() {
    initAudio(); // Unblock audio context
    document.getElementById('start-overlay').style.display = 'none';
    
    // Test speak to confirm initialization
    const utterance = new SpeechSynthesisUtterance("Kitchen system ready. Voice notifications enabled.");
    const voices = window.speechSynthesis.getVoices();
    const indianVoice = voices.find(v => v.lang === 'en-IN' || v.lang === 'hi-IN') || voices[0];
    if (indianVoice) utterance.voice = indianVoice;
    window.speechSynthesis.speak(utterance);
    
    console.log("Kitchen session started and audio unblocked.");
}

// Ensure voices are loaded
window.speechSynthesis.onvoiceschanged = () => {
    console.log("Voices loaded:", window.speechSynthesis.getVoices().length);
};

// Global click to ensure audio is unblocked if overlay is missed
document.addEventListener('click', () => {
    const overlay = document.getElementById('start-overlay');
    if (overlay && overlay.style.display !== 'none') {
        startKitchen();
    }
}, { once: true });

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

        // Detect new orders for sound and speech
        let newOrders = [];
        const currentIds = new Set(orders.map(o => o.id));

        if (isInitialized) {
            orders.forEach(o => {
                if (!lastKnownOrderIds.has(o.id)) {
                    newOrders.push(o);
                }
            });
        }

        if (newOrders.length > 0) {
            playBellSound();
            newOrders.forEach(o => speakOrder(o));
        }

        isInitialized = true;

        // Check for late orders (> 5 mins)
        const now = new Date();
        orders.forEach(o => {
            if (o.timestamp) {
                const orderTime = new Date(o.timestamp);
                const diffMs = now - orderTime;
                const diffMins = diffMs / 60000;

                // If late and hasn't alerted yet
                if (diffMins > 5 && !alertedOrderIds.has(o.id)) {
                    console.log(`Order ${o.id} is late (> 5m)`);
                    playBellSound();
                    alertedOrderIds.add(o.id);
                }
            }
        });

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
                        <li class="flex justify-between items-center text-lg border-b border-gray-100 last:border-0 py-2">
                            <div class="flex items-center">
                                ${i.image_url ? `<img src="${i.image_url}" class="w-12 h-12 rounded object-cover mr-3 border border-gray-200">` : ''}
                                <div class="flex flex-col">
                                    <span class="font-bold text-gray-800">${i.name_hindi || i.name}</span>
                                    ${i.name_hindi ? `<span class="text-xs text-gray-400">${i.name}</span>` : ''}
                                </div>
                            </div>
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

// Poll every 5 seconds
setInterval(fetchOrders, 5000);
fetchOrders();
