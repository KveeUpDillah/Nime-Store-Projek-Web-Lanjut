const rawData = JSON.parse(document.getElementById('cart-data').textContent);
const CATALOG = rawData;

/* ══════════════════════════════════════
   STATE  (mirrors Django models)
══════════════════════════════════════ */
const state = {
  // Checkout model fields
  checkout: {
    recipient_name: '',
    phone_number: '',
    address: '',
    city: '',
    province: '',
    postal_code: '',
    notes: '',
    status: 'waiting_payment',
  },
  // Payment model fields
  payment: {
    reference_id: null,
    amount: 0,
    status: 'pending',
    qris_image_url: null,
    qris_string: 'DUMMY-QRIS-STRING-12345',
    expired_at: null,
    paid_at: null,
  },
  // Cart: array of { product_id, qty }
cart: rawData.map(p => ({ product_id: p.id, qty: p.qty })),
  shipping: { method: 'reguler', cost: 15000 },
  voucher: { code: null, discount: 0 },
};

/* ── Helpers ── */
const fmt  = n => 'Rp ' + Number(n).toLocaleString('id-ID');
const uuid = () => ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
  (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));
const ONGKIR   = { reguler: 15000, express: 35000, same_day: 55000 };
const VOUCHERS = { 'HEMAT10': 0.10, 'DISKON50K': 50000, 'COBA': 25000 };

/* ── Computed subtotal from cart ── */
function calcSubtotal() {
  return state.cart.reduce((sum, item) => {
    const p = CATALOG.find(c => c.id === item.product_id);
    return sum + (p ? p.price_unit * item.qty : 0);
  }, 0);
}



/* ══════════════════════════════════════
   RENDER ORDER ITEMS
══════════════════════════════════════ */
function renderOrderItems() {
  const wrap  = document.getElementById('orderItems');
  const empty = document.getElementById('emptyState');
  const nums  = document.getElementById('summaryNumbers');
  const vrow  = document.getElementById('voucherRow');

  if (state.cart.length === 0) {
    wrap.innerHTML = '';
    wrap.appendChild(empty);
    empty.style.display = '';
    nums.style.display  = 'none';
    vrow.style.display  = 'none';
    document.getElementById('itemCount').textContent = '0 item';
    return;
  }

  // hide empty state, show number section
  empty.style.display = 'none';
  nums.style.display  = '';
  vrow.style.display  = '';

  // build items HTML
  const html = state.cart.map(item => {
    const p = CATALOG.find(c => c.id === item.product_id);
    if (!p) return '';
    const lineTotal = p.price_unit * item.qty;
    return `
      <div class="order-item" id="row-${p.id}">
        <div class="item-img"><i class="bi ${p.icon}"></i></div>
        <div class="flex-grow-1" style="min-width:0">
          <div class="item-name">${p.name}</div>
          <div class="item-meta">${p.variant}</div>
          <div class="mt-1">
            <div class="qty-stepper">
              <button onclick="changeQty('${p.id}',-1)" ${item.qty<=1?'disabled':''}><i class="bi bi-dash"></i></button>
              <span class="qty-val">${item.qty}</span>
              <button onclick="changeQty('${p.id}',+1)"><i class="bi bi-plus"></i></button>
            </div>
          </div>
        </div>
        <div class="d-flex flex-column align-items-end gap-1">
          <div class="item-price">${fmt(lineTotal)}</div>
          <div style="font-size:.71rem;color:var(--clr-muted)">${fmt(p.price_unit)} / pcs</div>
          <button class="btn-remove" onclick="removeFromCart('${p.id}')" title="Hapus"><i class="bi bi-trash3"></i></button>
        </div>
      </div>`;
  }).join('');

  // replace content but keep emptyState node
  wrap.innerHTML = html;

  // update count badge
  const totalQty = state.cart.reduce((s,i) => s + i.qty, 0);
  document.getElementById('itemCount').textContent = totalQty + ' item';

  updateTotal();
}

/* ══════════════════════════════════════
   CART ACTIONS
══════════════════════════════════════ */

function changeQty(productId, delta) {
  const item = state.cart.find(c => c.product_id === productId);
  if (!item) return;
  item.qty = Math.max(1, item.qty + delta);
  renderOrderItems();
  // re-render sim grid in case qty went back up from 0
}

function removeFromCart(productId) {
  state.cart = state.cart.filter(c => c.product_id !== productId);
  renderOrderItems();
  // reset voucher if cart now empty
  if (state.cart.length === 0) {
    state.voucher = { code: null, discount: 0 };
    document.getElementById('voucherInput').value = '';
    document.getElementById('voucherMsg').innerHTML = '';
  }
}

/* ══════════════════════════════════════
   UPDATE TOTAL UI
══════════════════════════════════════ */
function updateTotal() {
  const subtotal = calcSubtotal();
  const discount = state.voucher.discount;
  const total    = Math.max(0, subtotal + state.shipping.cost - discount);
  state.payment.amount = total;
  document.getElementById('ongkir').textContent   = fmt(state.shipping.cost);
  document.getElementById('subtotal').textContent  = fmt(subtotal);
  document.getElementById('diskon').textContent    = '- ' + fmt(discount);
  document.getElementById('totalBayar').textContent = fmt(total);
  document.getElementById('modalAmount').textContent = fmt(total);
}

/* ══════════════════════════════════════
   SHIPPING OPTION SELECTION
══════════════════════════════════════ */
document.querySelectorAll('.shipping-opt input[type=radio]').forEach(radio => {
  radio.addEventListener('change', () => {
    document.querySelectorAll('.shipping-opt').forEach(el => {
      el.style.borderColor = 'var(--clr-border)';
      el.style.background  = '';
    });
    const lbl = radio.closest('label');
    lbl.style.borderColor = 'var(--clr-brand)';
    lbl.style.background  = 'var(--clr-brand-lt)';
    state.shipping.method = radio.value;
    state.shipping.cost   = ONGKIR[radio.value];
    updateTotal();
  });
});
document.querySelector('.shipping-opt input:checked').closest('label').style.borderColor = 'var(--clr-brand)';
document.querySelector('.shipping-opt input:checked').closest('label').style.background  = 'var(--clr-brand-lt)';

/* ══════════════════════════════════════
   VOUCHER
══════════════════════════════════════ */
document.getElementById('applyVoucher').addEventListener('click', () => {
  const code = document.getElementById('voucherInput').value.trim().toUpperCase();
  const msg  = document.getElementById('voucherMsg');
  if (!code) { msg.innerHTML = ''; return; }
  const subtotal = calcSubtotal();
  if (VOUCHERS[code] !== undefined) {
    const v = VOUCHERS[code];
    state.voucher.code     = code;
    state.voucher.discount = v < 1 ? Math.floor(subtotal * v) : Math.min(v, subtotal);
    msg.innerHTML = `<span style="color:var(--clr-success)"><i class="bi bi-check-circle me-1"></i>Voucher <strong>${code}</strong> berhasil! Hemat ${fmt(state.voucher.discount)}</span>`;
  } else {
    state.voucher = { code: null, discount: 0 };
    msg.innerHTML = `<span style="color:var(--clr-danger)"><i class="bi bi-x-circle me-1"></i>Kode voucher tidak valid.</span>`;
  }
  updateTotal();
});

/* ══════════════════════════════════════
   FORM VALIDATION
══════════════════════════════════════ */
function validateForm() {
  const form = document.getElementById('checkoutForm');
  const fields = ['recipientName','phoneNumber','address','province','city','postalCode'];
  let valid = true;
  fields.forEach(id => {
    const el = document.getElementById(id);
    if (!el.value.trim()) {
      el.classList.add('is-invalid');
      valid = false;
    } else {
      el.classList.remove('is-invalid');
    }
  });
  if (!valid) form.reportValidity();
  return valid;
}

// Live clear
['recipientName','phoneNumber','address','province','city','postalCode'].forEach(id => {
  document.getElementById(id).addEventListener('input', function() {
    if (this.value.trim()) this.classList.remove('is-invalid');
  });
});

/* ══════════════════════════════════════
   BUAT PESANAN
══════════════════════════════════════ */
const qrisModal   = new bootstrap.Modal(document.getElementById('qrisModal'));
const successModal = new bootstrap.Modal(document.getElementById('successModal'));

document.getElementById('placeOrderBtn').addEventListener('click', () => {
  if (state.cart.length === 0) {
    const btn = document.getElementById('placeOrderBtn');
    btn.classList.add('btn-danger');
    btn.innerHTML = '<i class="bi bi-exclamation-triangle me-1"></i>Keranjang masih kosong!';
    setTimeout(() => {
      btn.classList.remove('btn-danger');
      btn.innerHTML = '<i class="bi bi-lock-fill me-1"></i> Buat Pesanan & Bayar';
    }, 2000);
    return;
  }
  if (!validateForm()) return;

  // Simulasi: set reference_id dan expired_at (dari backend biasanya)
  state.payment.reference_id = uuid();
  state.payment.status = 'pending';
  const exp = new Date(Date.now() + 30 * 60 * 1000); // +30 menit
  state.payment.expired_at = exp;

  // Tampilkan card status pembayaran
  const card = document.getElementById('paymentStatusCard');
  card.classList.remove('d-none');
  document.getElementById('refIdDisplay').textContent = state.payment.reference_id.slice(0,18) + '…';
  document.getElementById('expiredAtDisplay').textContent = exp.toLocaleTimeString('id-ID', { hour:'2-digit', minute:'2-digit' });

  // Update step indicator
  document.getElementById('step-pengiriman').classList.remove('active');
  document.getElementById('step-pengiriman').classList.add('done');
  document.getElementById('step-pengiriman').querySelector('.step-num').className = 'step-num done';
  document.getElementById('step-pengiriman').querySelector('.step-num').innerHTML = '<i class="bi bi-check"></i>';
  document.getElementById('step-pembayaran').classList.add('active');
  document.getElementById('step-pembayaran').querySelector('.step-num').className = 'step-num active';

  // Update QRIS modal content
  document.getElementById('modalRef').textContent = 'REF: ' + state.payment.reference_id.slice(0,18) + '…';
  document.getElementById('qrisImage').src =
    `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(state.payment.qris_string)}&color=1A56DB`;
  updateTotal();

  // Sembunyikan tombol buat pesanan
  document.getElementById('placeOrderBtn').innerHTML = '<i class="bi bi-check-circle me-1"></i>Pesanan Dibuat';
  document.getElementById('placeOrderBtn').disabled = true;

  // Buka modal QRIS langsung
  startCountdown(exp);

  const formData = new FormData();
  formData.append('recipient_name', document.getElementById('recipientName').value.trim());
  formData.append('phone_number', '+62' + document.getElementById('phoneNumber').value.trim());
  formData.append('address', document.getElementById('address').value.trim());
  formData.append('province', document.getElementById('province').value.trim());
  formData.append('city', document.getElementById('city').value.trim());
  formData.append('postal_code', document.getElementById('postalCode').value.trim());
  formData.append('notes', document.getElementById('notes').value.trim());

  fetch("{% url 'place_order' %}", {
    method: 'POST',
    headers: { 'X-CSRFToken': '{{ csrf_token }}' },
    body: formData
});
  qrisModal.show();
});

/* ── Open QRIS button (dari card status) ── */
document.getElementById('openQrisBtn').addEventListener('click', () => {
  startCountdown(state.payment.expired_at);
  qrisModal.show();
});

/* ══════════════════════════════════════
   COUNTDOWN TIMER
══════════════════════════════════════ */
let countdownInterval = null;
function startCountdown(expiredAt) {
  if (countdownInterval) clearInterval(countdownInterval);
  const el = document.getElementById('timerDisplay');
  const wrap = document.getElementById('countdown');
  function tick() {
    const diff = expiredAt - Date.now();
    if (diff <= 0) {
      clearInterval(countdownInterval);
      state.payment.status = 'expired';
      el.textContent = 'Kedaluwarsa';
      wrap.classList.add('expired');
      updateStatusBadge('expired');
      return;
    }
    const m = Math.floor(diff / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    el.textContent = `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  }
  tick();
  countdownInterval = setInterval(tick, 1000);
}

/* ══════════════════════════════════════
   UPDATE STATUS BADGE
══════════════════════════════════════ */
const STATUS_MAP = {
  pending:   { cls: 'status-pending',   label: 'Menunggu Pembayaran' },
  paid:      { cls: 'status-paid',      label: 'Sudah Dibayar' },
  expired:   { cls: 'status-expired',   label: 'Kedaluwarsa' },
  cancelled: { cls: 'status-cancelled', label: 'Dibatalkan' },
};
function updateStatusBadge(status) {
  const badge = document.getElementById('statusBadgeDisplay');
  const map = STATUS_MAP[status];
  badge.className = 'status-badge ' + map.cls;
  badge.innerHTML = `<span class="dot" style="width:6px;height:6px;border-radius:50%;background:currentColor;display:inline-block"></span> ${map.label}`;
}

/* ══════════════════════════════════════
   SIMULASI BAYAR
══════════════════════════════════════ */
document.getElementById('simulatePaidBtn').addEventListener('click', () => {
  clearInterval(countdownInterval);
  state.payment.status = 'paid';
  state.payment.paid_at = new Date();
  state.checkout.status = 'processing';

  qrisModal.hide();

  // Update step
  document.getElementById('step-pembayaran').classList.remove('active');
  document.getElementById('step-pembayaran').classList.add('done');
  document.getElementById('step-pembayaran').querySelector('.step-num').className = 'step-num done';
  document.getElementById('step-pembayaran').querySelector('.step-num').innerHTML = '<i class="bi bi-check"></i>';
  document.getElementById('step-selesai').classList.add('active');
  document.getElementById('step-selesai').querySelector('.step-num').className = 'step-num active';

  updateStatusBadge('paid');
  document.getElementById('openQrisBtn').innerHTML = '<i class="bi bi-check-circle me-1"></i>Pembayaran Diterima';
  document.getElementById('openQrisBtn').disabled = true;
  document.getElementById('openQrisBtn').style.background = 'var(--clr-success)';

  setTimeout(() => successModal.show(), 400);

  setTimeout(() => {
    successModal.show();
    // Tambah redirect setelah modal muncul sebentar
    setTimeout(() => {
        window.location.href = "{% url 'cust_orders' %}";  
    }, 2000);
  }, 400);
});

renderOrderItems();