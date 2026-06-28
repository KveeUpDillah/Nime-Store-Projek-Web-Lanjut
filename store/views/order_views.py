from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from xhtml2pdf import pisa
from store.models import Cart, CartItem, Order, OrderItem, Checkout, Payment, SellerProfile


def is_seller(user):
    return hasattr(user, 'seller_profile')


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_items')

        if not selected_ids:
            messages.error(request, 'Tidak ada barang yang dipilih.')
            return redirect('cart_view')

        request.session['checkout_item_ids'] = selected_ids
        items = CartItem.objects.filter(id__in=selected_ids, cart=cart)
        total = sum(item.subtotal for item in items)

        return render(request, 'cart/checkout.html', {
            'items': items,
            'total': total,
        })

    item_ids = request.session.get('checkout_item_ids', [])
    items = CartItem.objects.filter(id__in=item_ids, cart=cart)
    total = sum(item.subtotal for item in items)

    return render(request, 'cart/checkout.html', {
        'items': items,
        'total': total,
    })


@login_required
def place_order(request):
    print("=== PLACE ORDER DIPANGGIL ===")

    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        item_ids = request.session.get('checkout_item_ids', [])
        selected_items = CartItem.objects.filter(cart=cart, id__in=item_ids)
        total = sum(item.subtotal for item in selected_items)

        payment = Payment.objects.create(amount=total)
        order = Order.objects.create(user=request.user, total_price=total)

        for item in selected_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        checkout = Checkout.objects.create(
            user=request.user,
            order=order,
            payment=payment,
            recipient_name=request.POST.get('recipient_name') or request.user.username,
            phone_number=request.POST.get('phone_number') or '-',
            address=request.POST.get('address') or '-',
            city=request.POST.get('city') or '-',
            province=request.POST.get('province') or '-',
            postal_code=request.POST.get('postal_code') or '-',
            notes=request.POST.get('notes') or ''
        )

        selected_items.delete()

        if 'checkout_item_ids' in request.session:
            del request.session['checkout_item_ids']

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


def cancel_order(request, checkout_id):
    checkout = get_object_or_404(Checkout, id=checkout_id, user=request.user)

    if request.method == "POST":
        if checkout.status == Checkout.CheckoutStatus.WAITING_PAYMENT:
            checkout.delete()

    return redirect("cust_orders")


@login_required
def cust_orders(request):
    checkouts = Checkout.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/cust_orders.html', {'checkouts': checkouts})


def _get_checkout_for_receipt(request, checkout_id):
    """
    Helper: ambil Checkout untuk struk, dengan validasi akses.
    Boleh diakses oleh customer pemilik atau seller yang punya produk di order tersebut.
    Hanya untuk status processing/shipped/delivered.
    """
    checkout = get_object_or_404(Checkout, id=checkout_id)

    is_buyer = (checkout.user_id == request.user.id)
    is_order_seller = False
    if is_seller(request.user):
        is_order_seller = OrderItem.objects.filter(
            order=checkout.order,
            product__seller=request.user.seller_profile
        ).exists()

    if not (is_buyer or is_order_seller):
        return None, HttpResponse('Tidak punya akses ke struk ini.', status=403)

    allowed_status = [
        Checkout.CheckoutStatus.PROCESSING,
        Checkout.CheckoutStatus.SHIPPED,
        Checkout.CheckoutStatus.DELIVERED,
    ]
    if checkout.status not in allowed_status:
        return None, HttpResponse('Struk belum tersedia untuk pesanan ini.', status=400)

    return checkout, None


@login_required
def receipt_data(request, checkout_id):
    checkout, error = _get_checkout_for_receipt(request, checkout_id)
    if error:
        return error

    order = checkout.order
    items = order.items.select_related('product').all()

    data = {
        'order_id': checkout.id,
        'checkout_id': checkout.id,
        'status': checkout.get_status_display(),
        'buyer': checkout.user.username,
        'recipient_name': checkout.recipient_name,
        'address': f"{checkout.address}, {checkout.city}, {checkout.province} {checkout.postal_code}",
        'created_at': checkout.created_at.strftime('%d %B %Y, %H:%M'),
        'paid_at': checkout.payment.paid_at.strftime('%d %B %Y, %H:%M') if checkout.payment and checkout.payment.paid_at else '-',
        'items': [
            {
                'name': item.product.name,
                'quantity': item.quantity,
                'price': "{:,.0f}".format(item.product.price).replace(",", "."),
                'subtotal': item.formatted_subtotal,
            }
            for item in items
        ],
        'total': order.formatted_total_price,
        'pdf_url': reverse('receipt_pdf', args=[checkout.id]),
    }
    return JsonResponse(data)


@login_required
def receipt_pdf(request, checkout_id):
    checkout, error = _get_checkout_for_receipt(request, checkout_id)
    if error:
        return error

    order = checkout.order
    items = order.items.select_related('product').all()

    context = {
        'checkout': checkout,
        'order': order,
        'items': items,
    }

    html = render_to_string('orders/receipts_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="struk_order_{checkout.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Gagal membuat PDF struk.', status=500)

    return response