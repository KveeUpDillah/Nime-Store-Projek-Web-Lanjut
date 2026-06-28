document.querySelectorAll('.btn-ubah-qty').forEach(button => {
    button.addEventListener('click', function() {
        const itemId = this.dataset.id;
        const aksi = this.dataset.aksi;
        
        fetch(`/cart/update/${itemId}/?aksi=${aksi}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const qtyElement = document.getElementById(`qty-${itemId}`);
                const subtotalElement = document.getElementById(`subtotal-${itemId}`);
                
                if (data.jumlah_baru === 0) {
                    location.reload();
                } else {
                    if (qtyElement) qtyElement.innerText = data.jumlah_baru;
                    if (subtotalElement) subtotalElement.innerText = 'Rp ' + data.subtotal_baru;
                }
            } else {
                alert('Gagal mengubah jumlah barang');
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

// 2. Logika Tombol Hapus
document.querySelectorAll('.btn-hapus-item').forEach(button => {
    button.addEventListener('click', function() {
        const itemId = this.dataset.id;
        const namaProduk = this.dataset.nama;
        
        Swal.fire({
            title: 'Apakah kamu yakin?',
            text: `Menghapus "${namaProduk}" dari keranjang?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Ya, Hapus!',
            cancelButtonText: 'Batal'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`{% url 'remove_from_cart' 0 %}`.replace('0', itemId), {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': '{{ csrf_token }}'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Terhapus!',
                            text: data.pesan,
                            showConfirmButton: false,
                            timer: 1500
                        });
                        
                        const barisTabel = document.getElementById(`cart-row-${itemId}`);
                        if (barisTabel) {
                            barisTabel.style.transition = 'all 0.5s ease';
                            barisTabel.style.opacity = '0';
                            setTimeout(() => {
                                barisTabel.remove();
                                syncSelectAll();
                                updateCheckoutButton();

                                const sisaBaris = document.querySelectorAll('tbody tr');
                                if (sisaBaris.length === 0 || (sisaBaris.length === 1 && sisaBaris[0].querySelector('td[colspan]'))) {
                                    location.reload();
                                }
                            }, 500);
                        }
                    } else {
                        Swal.fire('Gagal!', 'Terjadi kesalahan.', 'error');
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });
});

// 3. Logika Checkbox Select All & Per Item
const selectAll = document.getElementById('select-all');
const btnCheckout = document.getElementById('btn-checkout');

function getItemCheckboxes() {
    return document.querySelectorAll('.item-checkbox');
}

function updateCheckoutButton() {
    const anyChecked = [...getItemCheckboxes()].some(cb => cb.checked);
    btnCheckout.disabled = !anyChecked;
}

function syncSelectAll() {
    const checkboxes = getItemCheckboxes();
    selectAll.checked = checkboxes.length > 0 && [...checkboxes].every(cb => cb.checked);
    selectAll.indeterminate = [...checkboxes].some(cb => cb.checked) && !selectAll.checked;
}

selectAll.addEventListener('change', function() {
    getItemCheckboxes().forEach(cb => cb.checked = this.checked);
    updateCheckoutButton();
});

document.querySelector('tbody').addEventListener('change', function(e) {
    if (e.target.classList.contains('item-checkbox')) {
        syncSelectAll();
        updateCheckoutButton();
    }
});

// 4. Logika Tombol Checkout di Keranjang
document.getElementById('form-checkout').addEventListener('submit', function(e) {
    const checked = [...getItemCheckboxes()].filter(cb => cb.checked);
    if (checked.length === 0) {
        e.preventDefault();
        alert('Pilih minimal 1 barang!');
        return;
    }
    const container = document.getElementById('hidden-inputs');
    container.innerHTML = '';
    checked.forEach(cb => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'selected_items';
        input.value = cb.dataset.id;  // pakai data-id, bukan value checkbox
        container.appendChild(input);
    });
});