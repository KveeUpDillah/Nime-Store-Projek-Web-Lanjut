from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from store.decorators import seller_required
from store.models import SellerProfile, Product, OrderItem, Checkout, Review
from store.forms import SellerProfileForm, ProductForm, SellerProfileEditForm


def is_seller(user):
    return hasattr(user, 'seller_profile')


@login_required
def seller_dashboard(request):
    if not is_seller(request.user):
        messages.error(request, 'Kamu harus menjadi seller terlebih dahulu.')
        return redirect('seller/become_seller')

    seller = request.user.seller_profile
    products = Product.objects.filter(seller=seller).order_by('-created_at')

    order_items = (
        OrderItem.objects
        .filter(product__seller=seller)
        .select_related('order', 'order__checkout', 'product')
        .order_by('-order__checkout__created_at')
    )

    checkouts_dict = {}
    for item in order_items:
        checkout = getattr(item.order, 'checkout', None)
        if checkout is None:
            continue
        if checkout.id not in checkouts_dict:
            checkouts_dict[checkout.id] = {'checkout': checkout, 'items': []}
        checkouts_dict[checkout.id]['items'].append(item)

    seller_orders = list(checkouts_dict.values())

    return render(request, 'seller/seller_dashboard.html', {
        'seller': seller,
        'products': products,
        'seller_orders': seller_orders,
    })


@login_required
def confirm_payment(request, checkout_id):
    if not is_seller(request.user):
        messages.error(request, 'Kamu harus menjadi seller terlebih dahulu.')
        return redirect('become_seller')

    seller = request.user.seller_profile
    checkout = get_object_or_404(Checkout, id=checkout_id)

    is_owner = OrderItem.objects.filter(
        order=checkout.order,
        product__seller=seller
    ).exists()

    if not is_owner:
        messages.error(request, 'Pesanan ini bukan milik toko kamu.')
        return redirect('seller_dashboard')

    if request.method == 'POST':
        if checkout.status == Checkout.CheckoutStatus.WAITING_PAYMENT:
            with transaction.atomic():
                checkout = Checkout.objects.select_for_update().get(id=checkout.id)

                if checkout.status != Checkout.CheckoutStatus.WAITING_PAYMENT:
                    messages.error(request, 'Status checkout sudah berubah, coba refresh halaman.')
                    return redirect('seller_dashboard')

                order_items = OrderItem.objects.filter(
                    order=checkout.order
                ).select_related('product').select_for_update()

                for item in order_items:
                    if item.product.stock < item.quantity:
                        messages.error(
                            request,
                            f'Stok {item.product.name} tidak cukup ({item.product.stock} tersisa, butuh {item.quantity}).'
                        )
                        return redirect('seller_dashboard')

                for item in order_items:
                    product = item.product
                    product.stock -= item.quantity
                    if product.stock <= 0:
                        product.stock = 0
                    product.save(update_fields=['stock'])

                checkout.status = Checkout.CheckoutStatus.PROCESSING
                checkout.save(update_fields=['status', 'updated_at'])

            messages.success(request, f'Pembayaran untuk Order #{checkout.order.id} berhasil dikonfirmasi, stok telah diperbarui.')

    return redirect('seller_dashboard')


@seller_required
@login_required
def product_create(request):
    if not is_seller(request.user):
        return redirect('become_seller')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller_profile
            product.save()
            messages.success(request, 'Produk berhasil ditambahkan.')
            return redirect('seller_dashboard')
        else:
            print(form.errors)
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Tambah Produk'
    })


@seller_required
@login_required
def product_update(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        seller=request.user.seller_profile
    )

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produk berhasil diperbarui.')
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Edit Produk'
    })


@seller_required
@login_required
def product_delete(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        seller=request.user.seller_profile
    )

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produk berhasil dihapus.')
        return redirect('seller_dashboard')

    return render(request, 'products/product_confirm_delete.html', {'product': product})


@login_required
def my_seller_profile(request):
    seller = get_object_or_404(SellerProfile, user=request.user)
    products = Product.objects.filter(seller=seller).order_by('-created_at')

    return render(request, 'profile/my_seller_profile.html', {
        'seller': seller,
        'products': products
    })


@login_required
def edit_seller_profile(request):
    seller = get_object_or_404(SellerProfile, user=request.user)

    if request.method == 'POST':
        form = SellerProfileEditForm(request.POST, request.FILES, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil seller berhasil diperbarui.')
            return redirect('my_seller_profile')
    else:
        form = SellerProfileEditForm(instance=seller)

    return render(request, 'profile/edit_seller_profile.html', {'form': form})


def seller_profile(request, seller_id):
    seller = get_object_or_404(SellerProfile, id=seller_id, is_active=True)
    products = Product.objects.filter(seller=seller, is_active=True).order_by('-created_at')

    return render(request, 'profile/seller_profile.html', {
        'seller': seller,
        'products': products
    })


@staff_member_required(login_url='login')
def review_dashboard(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'admin/review_dashboard.html', {'reviews': reviews})