/* ===== Carrinho com localStorage ===== */

let cart = JSON.parse(localStorage.getItem('acai_cart')) || [];

function updateCartUI() {
    const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
    const totalPrice = cart.reduce((sum, item) => sum + item.subtotal, 0);

    const navCount = document.getElementById('nav-cart-count');
    const footerCount = document.getElementById('footer-cart-count');
    const footerTotal = document.getElementById('footer-total');
    if (navCount) navCount.textContent = totalItems;
    if (footerCount) footerCount.textContent = totalItems;
    if (footerTotal) footerTotal.textContent = `R$ ${totalPrice.toFixed(2)}`;

    const cartList = document.getElementById('carrinho-list');
    if (!cartList) return;
    if (cart.length === 0) {
        cartList.innerHTML = '<p class="text-muted text-center">Seu carrinho está vazio</p>';
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
                <div style="display:flex; align-items:center; gap:4px;">
                    <button onclick="changeQty(${index}, -1)" style="background:#6B21A8; color:#fff; border:none; border-radius:8px; width:28px; height:28px; cursor:pointer; font-size:0.9rem;">-</button>
                    <span style="color:#fff; font-weight:600; min-width:20px; text-align:center;">${item.qty}</span>
                    <button onclick="changeQty(${index}, 1)" style="background:#6B21A8; color:#fff; border:none; border-radius:8px; width:28px; height:28px; cursor:pointer; font-size:0.9rem;">+</button>
                    <span class="cart-item-price" style="margin-left:8px; min-width:60px;">R$ ${item.subtotal.toFixed(2)}</span>
                    <button class="cart-item-remove" onclick="removeFromCart(${index})" title="Remover" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:1.2rem; margin-left:4px;">×</button>
                </div>
            </div>
        `;
    });
    html += `<div class="d-flex justify-content-between mt-3 fw-bold" style="color: #fff; font-family: 'Inter', sans-serif;">
        <span>Subtotal:</span>
        <span style="color: #4ADE80;">R$ ${totalPrice.toFixed(2)}</span>
    </div>`;
    if (storeDeliveryFee) {
        html += `<div class="d-flex justify-content-between" style="color: #a1a1aa; font-family: 'Inter', sans-serif; font-size: 0.85rem;">
            <span>Taxa de entrega:</span>
            <span style="color: #4ADE80;">R$ ${storeDeliveryFee.toFixed(2)}</span>
        </div>`;
    }
    const totalWithFee = totalPrice + (storeDeliveryFee || 0);
    html += `<div class="d-flex justify-content-between mt-2 fw-bold" style="color: #fff; font-family: 'Inter', sans-serif; font-size: 1.1rem;">
        <span>Total:</span>
        <span style="color: #4ADE80;">R$ ${totalWithFee.toFixed(2)}</span>
    </div>`;
    cartList.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

let storeDeliveryFee = null;

function getStoreInfo(callback) {
    fetch('/')
        .then(r => r.text())
        .then(html => {
            const feeMatch = html.match(/Taxa de entrega.*?R$\s*([\d.]+)/i);
            storeDeliveryFee = feeMatch ? parseFloat(feeMatch[1]) : 5.00;
            callback();
        })
        .catch(() => {
            storeDeliveryFee = 5.00;
            callback();
        });
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
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.innerHTML = `
        <div class="toast show" role="alert" style="background-color: #6B21A8; color: #fff; border-radius: 12px;">
            <div class="toast-body" style="font-family: 'Inter', sans-serif;">${message}</div>
        </div>
    `;
    document.body.appendChild(toastContainer);
    setTimeout(() => toastContainer.remove(), 2500);
}

document.addEventListener('DOMContentLoaded', function() {
    updateCartUI();

    document.querySelectorAll('.btn-add-cart').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.dataset.id);
            const name = this.dataset.name;
            const price = parseFloat(this.dataset.price);
            const category = this.dataset.category;
            addToCart(id, name, price, category);
        });
    });

    const finalizarBtn = document.getElementById('btn-finalizar-pedido');
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
                    headers: { 'Content-Type': 'application/json' },
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
