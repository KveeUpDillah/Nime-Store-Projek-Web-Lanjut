document.querySelectorAll('.cancel-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        Swal.fire({
            title: 'Batalkan Pesanan?',
            text: 'Duit bisa dicari, merch limited punah menyesal',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Ya, Batalkan!',
            cancelButtonText: 'Tidak'
        }).then((result) => {
            if (result.isConfirmed) {
                form.submit();
            }
        });
    });
});

// ===================== LOGIC MODAL STRUK =====================
const receiptOverlay = document.getElementById('receiptOverlay');
const receiptPanelBody = document.getElementById('receiptPanelBody');
const closeReceiptPanel = document.getElementById('closeReceiptPanel');

function openReceiptPanel() {
    receiptOverlay.classList.add('show');
}

function closeReceiptPanelFn() {
    receiptOverlay.classList.remove('show');
}

closeReceiptPanel.addEventListener('click', closeReceiptPanelFn);

// Klik di luar modal (area overlay) untuk menutup
receiptOverlay.addEventListener('click', function(e) {
    if (e.target === receiptOverlay) {
        closeReceiptPanelFn();
    }
});

// Tombol Escape untuk menutup
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && receiptOverlay.classList.contains('show')) {
        closeReceiptPanelFn();
    }
});

document.querySelectorAll('.btn-lihat-struk').forEach(btn => {
    btn.addEventListener('click', function() {
        const checkoutId = this.dataset.checkoutId;

        receiptPanelBody.innerHTML = '<p class="text-muted mb-0">Memuat struk...</p>';
        openReceiptPanel();

        fetch(`/orders/${checkoutId}/receipt/`)
            .then(res => {
                if (!res.ok) {
                    throw new Error('Gagal memuat struk');
                }
                return res.json();
            })
            .then(data => {
                let itemsHtml = data.items.map(item => `
                    <tr>
                        <td>${item.name}</td>
                        <td class="text-end">${item.quantity}</td>
                        <td class="text-end">Rp ${item.price}</td>
                        <td class="text-end">Rp ${item.subtotal}</td>
                    </tr>
                `).join('');

                receiptPanelBody.innerHTML = `
                    <div class="receipt-row"><span>Order</span><span>#${data.order_id}</span></div>
                    <div class="receipt-row"><span>Status</span><span>${data.status}</span></div>
                    <div class="receipt-row"><span>Nama Pembeli</span><span>${data.buyer}</span></div>
                    <div class="receipt-row"><span>Nama Penerima</span><span>${data.recipient_name}</span></div>
                    <div class="receipt-row"><span>Alamat Pengiriman</span><span class="text-end">${data.address}</span></div>
                    <div class="receipt-row"><span>Tanggal Pesanan</span><span>${data.created_at}</span></div>
                    <div class="receipt-row"><span>Tanggal Dibayar</span><span>${data.paid_at}</span></div>

                    <table>
                        <thead>
                            <tr>
                                <th>Produk</th>
                                <th class="text-end">Qty</th>
                                <th class="text-end">Harga</th>
                                <th class="text-end">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${itemsHtml}
                        </tbody>
                    </table>

                    <div class="receipt-total">
                        <span>Total</span>
                        <span>Rp ${data.total}</span>
                    </div>

                    <a href="${data.pdf_url}" class="btn btn-dark btn-sm w-100 mt-3">
                        Download PDF
                    </a>
                `;
            })
            .catch(() => {
                receiptPanelBody.innerHTML = '<p class="text-danger mb-0">Gagal memuat struk. Coba lagi.</p>';
            });
    });
});