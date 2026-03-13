/**
 * order.js — Employee order page.
 *
 * Fetches available products, manages a cart, and submits orders to the API.
 * Redirects to login if no token is found.
 */

// ── Auth guard ────────────────────────────────────────────────────────────────
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = '/';
}

// ── State ─────────────────────────────────────────────────────────────────────
let products = [];
/** @type {{ [productId: number]: { quantity: number, name: string } }} */
let cart = {};

// ── Product fetching ──────────────────────────────────────────────────────────
async function fetchProducts() {
    try {
        const response = await fetch('/api/products', {
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.status === 401) {
            window.location.href = '/';
            return;
        }

        products = await response.json();
        renderProducts();
    } catch {
        showOrderError('Could not load products. Please refresh the page.');
    }
}

// ── Rendering ─────────────────────────────────────────────────────────────────
function renderProducts() {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';

    products.forEach((product, index) => {
        const qty  = cart[product.id]?.quantity ?? 0;
        const card = buildProductCard(product, qty, index);
        grid.appendChild(card);
    });

    updateCartBar();
}

/**
 * Build a product card DOM element.
 * @param {object} product  - Product data from the API.
 * @param {number} qty      - Current quantity in the cart.
 * @param {number} index    - Position in the list (used for stagger animation).
 * @returns {HTMLElement}
 */
function buildProductCard(product, qty, index) {
    const card = document.createElement('div');
    card.className = 'product-card bg-white rounded-[32px] p-4 flex flex-col justify-between h-auto cursor-pointer group relative overflow-hidden';
    card.style.animationDelay = `${index * 50}ms`;

    if (qty > 0) {
        card.classList.add('ring-2', 'ring-black');
    }

    const quantityControl = qty === 0
        ? `<button onclick="updateCart(event, ${product.id}, 1)"
               class="w-10 h-10 rounded-full bg-gray-100 text-gray-900 flex items-center justify-center font-bold text-xl hover:bg-gray-200 transition-transform active:scale-95">
               <span class="mb-0.5">+</span>
           </button>`
        : `<div class="flex items-center bg-gray-900 rounded-full px-1.5 py-1 shadow-md animate-[popIn_0.2s_ease-out]">
               <button onclick="updateCart(event, ${product.id}, -1)"
                   class="w-8 h-8 rounded-full text-white flex items-center justify-center hover:bg-gray-700 transition active:scale-90">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 12H6"/>
                   </svg>
               </button>
               <span class="w-8 text-center text-white font-bold text-base select-none tabular-nums">${qty}</span>
               <button onclick="updateCart(event, ${product.id}, 1)"
                   class="w-8 h-8 rounded-full text-white flex items-center justify-center hover:bg-gray-700 transition active:scale-90">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6"/>
                   </svg>
               </button>
           </div>`;

    card.innerHTML = `
        <div class="h-32 w-full flex items-center justify-center mb-3 bg-gray-50 rounded-[20px] group-hover:bg-gray-100 transition-colors duration-300 p-2">
            <img src="${product.image_url}" alt="${product.name}"
                 class="w-full h-full object-contain drop-shadow-md transition-transform duration-300 group-hover:scale-105">
        </div>
        <div class="flex flex-col flex-grow">
            <div class="mb-2">
                <h3 class="font-bold text-gray-900 text-lg leading-tight mb-0.5 tracking-tight">${product.name}</h3>
                <p class="text-gray-400 text-xs font-medium">Free</p>
            </div>
            <div class="mt-auto flex items-center justify-end">
                ${quantityControl}
            </div>
        </div>
    `;

    // Clicking anywhere on the card (not on a button) increments quantity
    card.onclick = (e) => {
        if (!e.target.closest('button')) {
            updateCart(e, product.id, 1);
        }
    };

    return card;
}

// ── Cart management ───────────────────────────────────────────────────────────
function updateCart(e, productId, delta) {
    if (e) e.stopPropagation();

    const product = products.find(p => p.id === productId);
    if (!product) return;

    if (!cart[productId]) {
        cart[productId] = { quantity: 0, name: product.name };
    }

    cart[productId].quantity += delta;

    if (cart[productId].quantity <= 0) {
        delete cart[productId];
    }

    renderProducts();
}

function updateCartBar() {
    const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
    const cartBar    = document.getElementById('cart-bar');

    if (totalItems > 0) {
        cartBar.classList.remove('hidden');
        cartBar.classList.add('flex', 'animate-[fadeUp_0.3s_ease-out]');
        document.getElementById('cart-count').textContent = totalItems;
    } else {
        cartBar.classList.add('hidden');
        cartBar.classList.remove('flex');
    }
}

// ── Place order ───────────────────────────────────────────────────────────────
document.getElementById('placeOrderBtn').addEventListener('click', async () => {
    const items = Object.entries(cart).map(([id, item]) => ({
        product_id: parseInt(id, 10),
        quantity:   item.quantity,
        name:       item.name,
        price:      0,
    }));

    if (items.length === 0) return;

    const notes = document.getElementById('order-notes').value.trim() || null;

    try {
        const response = await fetch('/api/order', {
            method: 'POST',
            headers: {
                'Content-Type':  'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ items, notes }),
        });

        if (response.ok) {
            cart = {};
            document.getElementById('order-notes').value = '';
            renderProducts();
            showSuccessModal();
        } else {
            showOrderError('Could not place your order. Please try again.');
        }
    } catch {
        showOrderError('Network error. Please check your connection and try again.');
    }
});

// ── Modals & feedback ─────────────────────────────────────────────────────────
function showSuccessModal() {
    const modal   = document.getElementById('successModal');
    const content = modal.querySelector('.modal-content');

    modal.classList.remove('hidden');
    void modal.offsetWidth; // Force reflow to trigger CSS transition

    modal.classList.remove('opacity-0');
    content.classList.add('modal-enter');
}

function closeModal() {
    const modal = document.getElementById('successModal');
    modal.classList.add('opacity-0');
    setTimeout(() => modal.classList.add('hidden'), 300);
}

function showOrderError(message) {
    // Reuse the error UI pattern from the modal overlay area
    let errEl = document.getElementById('order-error-msg');
    if (!errEl) {
        errEl = document.createElement('p');
        errEl.id = 'order-error-msg';
        errEl.className = 'fixed bottom-32 left-1/2 -translate-x-1/2 bg-red-600 text-white text-sm font-medium px-4 py-2 rounded-xl shadow-lg z-50';
        document.body.appendChild(errEl);
    }
    errEl.textContent = message;
    errEl.style.display = 'block';
    setTimeout(() => { errEl.style.display = 'none'; }, 4000);
}

// ── Logout ────────────────────────────────────────────────────────────────────
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = '/';
});

// ── Init ──────────────────────────────────────────────────────────────────────
fetchProducts();
