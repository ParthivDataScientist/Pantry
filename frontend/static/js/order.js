
let products = [];
let cart = {}; // { productId: { quantity, name } } (Removed price)
console.log("Order page loaded");
const token = localStorage.getItem('token');
console.log("Token present:", !!token);
if (!token) {
    console.warn("No token found, redirecting to login");
    window.location.href = '/';
}

async function fetchProducts() {
    try {
        const response = await fetch('/api/products', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.status === 401) {
            window.location.href = '/';
            return;
        }
        products = await response.json();
        renderProducts();
    } catch (e) {
        console.error("Failed to fetch products");
    }
}

function renderProducts() {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';

    products.forEach((p, index) => {
        const qty = cart[p.id] ? cart[p.id].quantity : 0;

        const card = document.createElement('div');
        card.className = 'product-card bg-white rounded-[32px] p-4 flex flex-col justify-between h-auto cursor-pointer group relative overflow-hidden';
        card.style.animationDelay = `${index * 50}ms`; // Staggered delay

        // Active state border if selected
        if (qty > 0) {
            card.classList.add('ring-2', 'ring-black');
        }

        card.innerHTML = `
            <div class="h-32 w-full flex items-center justify-center mb-3 bg-gray-50 rounded-[20px] group-hover:bg-gray-100 transition-colors duration-300 p-2">
                <img src="${p.image_url}" alt="${p.name}" class="w-full h-full object-contain drop-shadow-md transition-transform duration-300 group-hover:scale-105">
            </div>
            
            <div class="flex flex-col flex-grow">
                <div class="mb-2">
                    <h3 class="font-bold text-gray-900 text-lg leading-tight mb-0.5 tracking-tight">${p.name}</h3>
                    <p class="text-gray-400 text-xs font-medium">Free</p>
                </div>

                <div class="mt-auto flex items-center justify-end">
                    ${qty === 0 ? `
                        <button onclick="updateCart(event, ${p.id}, 1)" class="w-10 h-10 rounded-full bg-gray-100 text-gray-900 flex items-center justify-center font-bold text-xl hover:bg-gray-200 transition-transform active:scale-95">
                            <span class="mb-0.5">+</span>
                        </button>
                    ` : `
                        <div class="flex items-center bg-gray-900 rounded-full px-1.5 py-1 shadow-md animate-[popIn_0.2s_ease-out]">
                            <button onclick="updateCart(event, ${p.id}, -1)" class="w-8 h-8 rounded-full text-white flex items-center justify-center hover:bg-gray-700 transition active:scale-90">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 12H6"/></svg>
                            </button>
                            <span class="w-8 text-center text-white font-bold text-base select-none tabular-nums">${qty}</span>
                            <button onclick="updateCart(event, ${p.id}, 1)" class="w-8 h-8 rounded-full text-white flex items-center justify-center hover:bg-gray-700 transition active:scale-90">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6"/></svg>
                            </button>
                        </div>
                    `}
                </div>
            </div>
        `;

        // Make whole card clickable to add (unless clicking buttons)
        card.onclick = (e) => {
            if (e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
                updateCart(e, p.id, 1);
            }
        };

        grid.appendChild(card);
    });
    updateFooter();
}

function updateCart(e, id, change) {
    if (e) e.stopPropagation();

    const product = products.find(p => p.id === id);
    if (!cart[id]) cart[id] = { quantity: 0, name: product.name };

    cart[id].quantity += change;

    if (cart[id].quantity <= 0) {
        delete cart[id];
    }

    renderProducts();
}

function updateFooter() {
    const totalItems = Object.values(cart).reduce((acc, item) => acc + item.quantity, 0);
    const cartBar = document.getElementById('cart-bar');

    if (totalItems > 0) {
        cartBar.classList.remove('hidden');
        cartBar.classList.add('flex', 'animate-[fadeUp_0.3s_ease-out]');
        document.getElementById('cart-count').innerText = totalItems;
    } else {
        cartBar.classList.add('hidden');
        cartBar.classList.remove('flex');
    }
}

document.getElementById('placeOrderBtn').addEventListener('click', async () => {
    const items = Object.keys(cart).map(id => ({
        product_id: parseInt(id),
        quantity: cart[id].quantity,
        name: cart[id].name,
        price: 0
    }));

    if (items.length === 0) return;

    const employee = "me";
    const notes = document.getElementById('order-notes').value || "";

    try {
        const response = await fetch('/api/order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ employee, items, total: 0, notes })
        });

        if (response.ok) {
            showSuccessModal();
            cart = {};
            renderProducts();
        } else {
            alert("Failed to place order.");
        }
    } catch (e) {
        console.error(e);
    }
});

function showSuccessModal() {
    const modal = document.getElementById('successModal');
    const content = modal.querySelector('.modal-content');

    modal.classList.remove('hidden');
    void modal.offsetWidth;

    modal.classList.remove('opacity-0');
    content.classList.add('modal-enter');
}

function closeModal() {
    const modal = document.getElementById('successModal');
    modal.classList.add('opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
}

document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = '/';
});

fetchProducts();
