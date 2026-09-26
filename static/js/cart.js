/* ===== Carrinho com localStorage ===== */

let cart = JSON.parse(localStorage.getItem('acai_cart')) || [];
let storeDeliveryFee = 0;
let storeIsOpen = true;

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

function formatCurrency(value) {
    return `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;
}

function updateCartBadge(count) {
    const badges = document.querySelectorAll('.cart-badge');
    badges.forEach(b => {
        b.textContent = count;
        b.style.display = count > 0 ? 'inline-flex' : 'none';
    });
}

function updateCartUI() {
    const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
    const totalPrice = cart.reduce((sum, item) => sum + item.subtotal, 0);

    updateCartBadge(totalItems);

    const totalWithFee = totalPrice + storeDeliveryFee;
    const subtotalDisplay = document.getElementById('cart-subtotal');
    const deliveryFeeDisplay = document.getElementById('cart-delivery-fee');
    const totalDisplay = document.getElementById('cart-total-final');

    if (subtotalDisplay) subtotalDisplay.textContent = formatCurrency(totalPrice);
    if (deliveryFeeDisplay) deliveryFeeDisplay.textContent = storeDeliveryFee > 0 ? formatCurrency(storeDeliveryFee) : '–';
    if (totalDisplay) totalDisplay.textContent = formatCurrency(totalWithFee);

    const cartList = document.getElementById('cart-items-list');
    if (!cartList) return;
    if (cart.length === 0) {
        cartList.innerHTML = '<p class="cart-empty-msg">Seu carrinho está vazio 🍇</p>';
        return;
    }

    let html = '';
    cart.forEach((item, index) => {
        html += `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${escapeHtml(item.name)}</div>
                    <div class="cart-item-qty">${escapeHtml(item.category || '')} • Qtd: ${item.qty}</div>
                </div>
                <div class="cart-item-controls">
                    <div class="cart-qty-group">
                        <button class="cart-qty-button" onclick="changeQty(${index}, -1)">-</button>
                        <span style="font-weight:900; min-width:20px; text-align:center;">${item.qty}</span>
                        <button class="cart-qty-button" onclick="changeQty(${index}, 1)">+</button>
                    </div>
                    <span class="cart-item-price">${formatCurrency(item.subtotal)}</span>
                    <button class="cart-item-remove" onclick="removeFromCart(${index})" title="Remover">×</button>
                </div>
            </div>
        `;
    });
    cartList.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadStoreSettings() {
    try {
        const response = await fetch('/api/settings');
        if (!response.ok) throw new Error('Erro ao carregar configurações');

        const data = await response.json();
        const deliveryFee = Number(data.delivery_fee);
        storeDeliveryFee = Number.isFinite(deliveryFee) ? deliveryFee : 0;
        const isOpen = data.is_open;
        storeIsOpen = typeof isOpen === 'boolean' ? isOpen : true;
    } catch (e) {
        storeDeliveryFee = 0;
        storeIsOpen = true;
    }
}

function addToCart(productId, name, price, category) {
    const existing = cart.find(item => item.id === productId);
    if (existing) {
        existing.qty += 1;
        existing.subtotal = parseFloat((existing.qty * existing.price).toFixed(2));
    } else {
        cart.push({
            id: productId,
            name: name,
            price: price,
            category: category,
            qty: 1,
            subtotal: price
        });
    }
    localStorage.setItem('acai_cart', JSON.stringify(cart));
    updateCartUI();
    showToast(`${name} adicionado ao carrinho!`);
}

function changeQty(index, delta) {
    if (!cart[index]) return;
    cart[index].qty += delta;
    cart[index].subtotal = parseFloat((cart[index].qty * cart[index].price).toFixed(2));
    if (cart[index].qty <= 0) {
        cart.splice(index, 1);
    }
    localStorage.setItem('acai_cart', JSON.stringify(cart));
    updateCartUI();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem('acai_cart', JSON.stringify(cart));
    updateCartUI();
}

function clearCart() {
    cart = [];
    localStorage.setItem('acai_cart', JSON.stringify(cart));
    updateCartUI();
}

function showToast(message) {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    toastContainer.innerHTML = `
        <div class="toast show" role="alert">
            <div class="toast-body">${message}</div>
        </div>
    `;
    document.body.appendChild(toastContainer);
    setTimeout(() => toastContainer.remove(), 2500);
}

function openCart() {
    const sidebar = document.getElementById('cart-sidebar');
    const backdrop = document.getElementById('cart-backdrop');
    if (sidebar) {
        sidebar.classList.add('is-open');
        sidebar.setAttribute('aria-hidden', 'false');
    }
    if (backdrop) backdrop.classList.add('is-open');
    document.querySelectorAll('.js-cart-toggle').forEach(btn => {
        btn.setAttribute('aria-expanded', 'true');
    });
}

function closeCart() {
    const sidebar = document.getElementById('cart-sidebar');
    const backdrop = document.getElementById('cart-backdrop');
    if (sidebar) {
        sidebar.classList.remove('is-open');
        sidebar.setAttribute('aria-hidden', 'true');
    }
    if (backdrop) backdrop.classList.remove('is-open');
    document.querySelectorAll('.js-cart-toggle').forEach(btn => {
        btn.setAttribute('aria-expanded', 'false');
    });
}

function toggleCart() {
    const sidebar = document.getElementById('cart-sidebar');
    if (!sidebar) return;
    const isOpen = sidebar.classList.contains('is-open');
    if (isOpen) {
        closeCart();
    } else {
        openCart();
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    await loadStoreSettings();
    updateCartUI();

    document.querySelectorAll('.js-cart-toggle').forEach(btn => {
        btn.addEventListener('click', toggleCart);
    });

    const cartBackdrop = document.getElementById('cart-backdrop');
    if (cartBackdrop) cartBackdrop.addEventListener('click', closeCart);

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') closeCart();
    });

    document.querySelectorAll('.btn-add').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.dataset.id);
            const name = this.dataset.name;
            const price = parseFloat(this.dataset.price);
            const category = this.dataset.category;
            addToCart(id, name, price, category);
            this.classList.add('added');
            this.textContent = '✓';
            setTimeout(() => {
                this.classList.remove('added');
                this.textContent = '+';
            }, 1000);
        });
    });

    const finalizarBtn = document.getElementById('btn-whatsapp-order');
    if (finalizarBtn) {
        finalizarBtn.addEventListener('click', async function() {
            const nome = document.getElementById('cliente-nome').value.trim();
            const endereco = document.getElementById('cliente-endereco').value.trim();
            const observacoes = document.getElementById('cliente-observacoes').value.trim();

            if (!nome || !endereco) {
                showToast('Preencha nome e endereço para finalizar!');
                return;
            }
            if (cart.length === 0) {
                showToast('Seu carrinho está vazio!');
                return;
            }
            if (!storeIsOpen) {
                showToast('A loja está fechada no momento. Tente mais tarde!');
                return;
            }

            const itens = cart.map(item => ({
                product_id: item.id,
                nome: item.name,
                categoria: item.category,
                quantidade: item.qty,
                preco_unitario: item.price,
                subtotal: item.subtotal
            }));

            try {
                const response = await fetch('/pedido', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ nome, endereco, observacoes, itens })
                });
                const data = await response.json();
                if (data.success && data.wa_me_url) {
                    window.open(data.wa_me_url, '_blank');
                    clearCart();
                    showToast('Pedido enviado! Abra o WhatsApp para confirmar.');
                } else if (data.error) {
                    showToast(data.error);
                }
            } catch (e) {
                showToast('Erro ao enviar pedido. Tente novamente.');
            }
        });
    }
});
