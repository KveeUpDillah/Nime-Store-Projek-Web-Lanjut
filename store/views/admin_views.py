from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from store.models import (
    Category, Anime, Product, UserProfile, SellerProfile,
    Order, OrderItem, Checkout, Payment,
    Review, ProductReview, ReviewReply,
)

User = get_user_model()


def admin_required(view_func):
    return staff_member_required(view_func, login_url='/login/')


# ─── Dashboard ───────────────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Stat cards
    total_products   = Product.objects.count()
    total_orders     = Order.objects.count()
    monthly_revenue  = Order.objects.filter(
        created_at__gte=month_start
    ).aggregate(total=Sum('total_price'))['total'] or 0
    total_users      = User.objects.count()
    pending_payments = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()
    new_reviews      = ProductReview.objects.filter(created_at__gte=month_start).count()

    # Recent orders (5 latest)
    recent_orders = Order.objects.select_related('user', 'checkout').order_by('-created_at')[:5]

    # Checkout status breakdown (current month)
    checkout_stats = (
        Checkout.objects
        .filter(created_at__gte=month_start)
        .values('status')
        .annotate(count=Count('id'))
    )

    # Orders per month (last 6 months) for chart
    months = []
    for i in range(5, -1, -1):
        d = (now - timedelta(days=30 * i)).replace(day=1)
        label = d.strftime('%b')
        count = Order.objects.filter(
            created_at__year=d.year,
            created_at__month=d.month
        ).count()
        months.append({'label': label, 'count': count})
    max_count = max((m['count'] for m in months), default=1) or 1

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'monthly_revenue': monthly_revenue,
        'total_users': total_users,
        'pending_payments': pending_payments,
        'new_reviews': new_reviews,
        'recent_orders': recent_orders,
        'checkout_stats': checkout_stats,
        'months': months,
        'max_count': max_count,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ─── Produk ──────────────────────────────────────────────────────────────────

@admin_required
def admin_products(request):
    qs = Product.objects.select_related('seller', 'category', 'anime').order_by('-created_at')
    category_filter = request.GET.get('category')
    status_filter   = request.GET.get('status')
    if category_filter:
        qs = qs.filter(category_id=category_filter)
    if status_filter == 'active':
        qs = qs.filter(is_active=True)
    elif status_filter == 'inactive':
        qs = qs.filter(is_active=False)
    categories = Category.objects.all()
    return render(request, 'admin_panel/products.html', {
        'products': qs, 'categories': categories,
    })


@admin_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
    return redirect('admin_products')


# ─── Kategori ────────────────────────────────────────────────────────────────

@admin_required
def admin_categories(request):
    categories = Category.objects.annotate(product_count=Count('product')).order_by('name')
    return render(request, 'admin_panel/categories.html', {'categories': categories})


@admin_required
def admin_category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Category.objects.create(name=name)
        return redirect('admin_categories')
    return render(request, 'admin_panel/category_form.html', {'category': None})


@admin_required
def admin_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.save()
        return redirect('admin_categories')
    return render(request, 'admin_panel/category_form.html', {'category': category})


@admin_required
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
    return redirect('admin_categories')


# ─── Anime ───────────────────────────────────────────────────────────────────

@admin_required
def admin_anime(request):
    anime_list = Anime.objects.all().order_by('title')
    return render(request, 'admin_panel/anime.html', {'anime_list': anime_list})


@admin_required
def admin_anime_delete(request, pk):
    anime = get_object_or_404(Anime, pk=pk)
    if request.method == 'POST':
        anime.delete()
    return redirect('admin_anime')


# ─── Order ───────────────────────────────────────────────────────────────────

@admin_required
def admin_orders(request):
    orders = Order.objects.select_related('user', 'checkout').order_by('-created_at')
    return render(request, 'admin_panel/orders.html', {'orders': orders})


@admin_required
def admin_order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('user', 'checkout', 'checkout__payment')
                     .prefetch_related('items__product'),
        pk=pk
    )
    return render(request, 'admin_panel/order_detail.html', {'order': order})


@admin_required
def admin_order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
    return redirect('admin_orders')


# ─── Checkout ────────────────────────────────────────────────────────────────

@admin_required
def admin_checkouts(request):
    qs = Checkout.objects.select_related('user', 'order', 'payment').order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'admin_panel/checkouts.html', {
        'checkouts': qs,
        'statuses': Checkout.CheckoutStatus.choices,
    })


@admin_required
def admin_checkout_update_status(request, pk):
    checkout = get_object_or_404(Checkout, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Checkout.CheckoutStatus.choices):
            checkout.status = new_status
            checkout.save()
    return redirect('admin_checkouts')


@admin_required
def admin_checkout_delete(request, pk):
    checkout = get_object_or_404(Checkout, pk=pk)
    if request.method == 'POST':
        checkout.delete()
    return redirect('admin_checkouts')


# ─── Pembayaran ──────────────────────────────────────────────────────────────

@admin_required
def admin_payments(request):
    qs = Payment.objects.select_related('checkout').order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'admin_panel/payments.html', {
        'payments': qs,
        'statuses': Payment.PaymentStatus.choices,
    })


@admin_required
def admin_payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
    return redirect('admin_payments')


# ─── User ────────────────────────────────────────────────────────────────────

@admin_required
def admin_users(request):
    users = User.objects.select_related('user_profile').order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})


@admin_required
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user.pk == request.user.pk:
            # Cegah admin menghapus akun dirinya sendiri yang sedang login
            return redirect('admin_users')
        user.delete()
    return redirect('admin_users')


# ─── Seller ──────────────────────────────────────────────────────────────────

@admin_required
def admin_sellers(request):
    sellers = SellerProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'admin_panel/sellers.html', {'sellers': sellers})


@admin_required
def admin_seller_toggle(request, pk):
    seller = get_object_or_404(SellerProfile, pk=pk)
    if request.method == 'POST':
        seller.is_active = not seller.is_active
        seller.save()
    return redirect('admin_sellers')


@admin_required
def admin_seller_delete(request, pk):
    seller = get_object_or_404(SellerProfile, pk=pk)
    if request.method == 'POST':
        seller.delete()
    return redirect('admin_sellers')


# ─── Review ──────────────────────────────────────────────────────────────────

@admin_required
def admin_reviews(request):
    product_reviews = ProductReview.objects.select_related(
        'product', 'user'
    ).prefetch_related('images', 'reply').order_by('-created_at')

    general_reviews = Review.objects.order_by('-created_at')

    return render(request, 'admin_panel/reviews.html', {
        'product_reviews': product_reviews,
        'general_reviews': general_reviews,
    })


@admin_required
def admin_review_toggle_visibility(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.is_visible = not review.is_visible
        review.save()
    return redirect('admin_reviews')


@admin_required
def admin_review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
    return redirect('admin_reviews')


@admin_required
def admin_product_review_delete(request, pk):
    review = get_object_or_404(ProductReview, pk=pk)
    if request.method == 'POST':
        review.delete()
    return redirect('admin_reviews')