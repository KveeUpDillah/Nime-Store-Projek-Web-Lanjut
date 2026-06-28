from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from store.models import Cart, CartItem, Product


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.user == product.seller:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'pesan': 'Anda tidak dapat menambahkan produk milik sendiri ke keranjang.'
            })
        messages.error(request, 'Anda tidak dapat menambahkan produk milik sendiri ke keranjang.')
        return redirect('product_detail', product_id=product.id)

    if product.stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'pesan': 'Stok produk habis.'})
        messages.error(request, 'Stok produk habis.')
        return redirect('product_detail', product_id=product.id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'pesan': 'Gagal menambahkan! Jumlah di keranjang sudah mencapai batas stok.'
                })
            messages.error(request, 'Jumlah di keranjang sudah mencapai batas stok.')
            return redirect('cart/cart')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'pesan': f'{product.name} berhasil ditambahkan ke keranjang!'
        })

    messages.success(request, 'Produk berhasil ditambahkan ke keranjang.')
    return redirect('cart/cart')


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    product = cart_item.product
    aksi = request.GET.get('aksi')

    if aksi == 'tambah':
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
    elif aksi == 'kurang':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'jumlah_baru': 0})
            return redirect('cart/cart')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'jumlah_baru': cart_item.quantity,
            'subtotal_baru': cart_item.formatted_subtotal,
        })

    return redirect('cart/cart')


@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    nama_produk = item.product.name

    if request.method == 'POST':
        item.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'pesan': f'"{nama_produk}" berhasil dihapus dari keranjang.'
            })
        messages.success(request, 'Produk berhasil dihapus dari keranjang.')

    return redirect('cart/cart')