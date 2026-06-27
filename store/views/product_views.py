from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, Value, IntegerField
from store.models import Product, Anime, Category, ProductReview, ProductReviewImage
from store.forms import ProductReviewForm, ReplyForm

def catalog(request):
    query = request.GET.get('q', '')
    anime_id = request.GET.get('anime', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(seller__shop_name__icontains=query) |
            Q(seller__user__username__icontains=query) |
            Q(anime__title__icontains=query)
        )

    if anime_id:
        products = products.filter(anime_id=anime_id)

    if category_id:
        products = products.filter(category_id=category_id)

    try:
        if min_price:
            products = products.filter(price__gte=int(min_price))
        if max_price:
            products = products.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass

    anime_list = Anime.objects.all().order_by('title')
    category_list = Category.objects.all().order_by('name')

    products = products.annotate(
        is_sold_out_order=Case(
            When(stock__lte=0, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('is_sold_out_order', '-created_at')

    return render(request, 'products/catalog.html', {
        'products': products,
        'query': query,
        'anime_id': anime_id,
        'category_id': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'anime_list': anime_list,
        'category_list': category_list,
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = ProductReview.objects.filter(product=product).order_by('-created_at')
    review_form = ProductReviewForm()

    user_review = None
    can_review = False

    if request.user.is_authenticated:
        user_review = ProductReview.objects.filter(
            product=product,
            user=request.user
        ).first()

        can_review = (
            request.user != product.seller.user
            and user_review is None
        )

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'user_review': user_review,
        'can_review': can_review,
    })


@login_required
def add_product_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.user == product.seller.user:
        messages.error(request, "Penjual tidak dapat memberikan ulasan pada produknya sendiri.")
        return redirect('product_detail', product_id=product.id)

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        images = request.FILES.getlist('images')

        if len(images) > 3:
            messages.error(request, 'Maksimal upload 3 foto.')
            return redirect('product_detail', product_id=product.id)

        for image in images:
            if not image.content_type.startswith('image/'):
                messages.error(request, 'Semua file harus berupa gambar.')
                return redirect('product_detail', product_id=product.id)

        if form.is_valid():
            review, created = ProductReview.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment']
                }
            )

            review.images.all().delete()

            for image in images:
                ProductReviewImage.objects.create(review=review, image=image)

            messages.success(request, 'Ulasan produk berhasil dikirim.')
            return redirect('product_detail', product_id=product.id)

    return redirect('product_detail', product_id=product.id)


@login_required
def reply_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id)

    if request.user != review.product.seller.user:
        messages.error(request, "Anda tidak memiliki izin untuk membalas ulasan ini.")
        return redirect("product_detail", product_id=review.product.id)

    if hasattr(review, "reply"):
        messages.warning(request, "Ulasan ini sudah memiliki balasan.")
        return redirect("product_detail", product_id=review.product.id)

    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.review = review
            reply.seller = request.user
            reply.save()
            messages.success(request, "Balasan berhasil dikirim.")

    return redirect("product_detail", product_id=review.product.id)