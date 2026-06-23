import requests
import re
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from store.decorators import moderator_required, seller_required, customer_required
from store.permission import is_moderator
from store.models import Product
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Review, SellerProfile, Product, ProductReview, Cart, CartItem, UserProfile, Anime, Category
from .forms import ReviewForm, SellerProfileForm, ProductForm, ProductReviewForm, UserProfileForm, SellerProfileEditForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import Group
from django.http import JsonResponse
from .chatbox import ask_ai, SYSTEM_PROMPT, BLOCKED_KEYWORDS

def index(request):
    products = Product.objects.all()
    return render(request, 'layouts/index.html', {'products': products})

def home(request):
    reviews = Review.objects.filter(is_visible=True).order_by('-created_at')[:6]

    return render(request, 'pages/home.html', {
        'reviews': reviews
    })


def support(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Review berhasil dikirim. Terima kasih!')
            return redirect('support')
    else:
        form = ReviewForm()

    return render(request, 'pages/support.html', {
        'form': form
    })

def contact(request):
    return render(request, 'pages/contact.html')

def gallery(request):   
    return render(request, 'pages/gallery.html')

def support(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Review berhasil dikirim. Terima kasih!')
            return redirect('support')
    else:
        form = ReviewForm()

    return render(request, 'pages/support.html', {
        'form': form
    })

def about(request):
    return render(request, 'pages/about.html')

def login(request):
    return render(request, 'accounts/login.html')

# Dashboard view, hanya bisa diakses admin
@moderator_required
@login_required
@user_passes_test(is_moderator)
def dashboard(request):
    return render(request, 'admin/dashboard.html')

def is_seller(user):
    return hasattr(user, 'seller_profile')

@customer_required
@login_required
def become_seller(request):
    if is_seller(request.user):
        return redirect('seller_dashboard')

    if request.method == 'POST':
        form = SellerProfileForm(request.POST)

        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            seller.save()
            seller_group = Group.objects.get(name='Seller')
            request.user.groups.add(seller_group)


            messages.success(request, 'Akun seller berhasil dibuat.')
            return redirect('seller_dashboard')
    else:
        form = SellerProfileForm()

    return render(request, 'seller/become_seller.html', {
        'form': form
    })

@login_required
def seller_dashboard(request):
    if not is_seller(request.user):
        messages.error(request, 'Kamu harus menjadi seller terlebih dahulu.')
        return redirect('seller/become_seller')

    seller = request.user.seller_profile
    products = Product.objects.filter(seller=seller).order_by('-created_at')

    return render(request, 'seller/seller_dashboard.html', {
        'seller': seller,
        'products': products
    })

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
            print(form.errors)  # <-- taruh di sini
    
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

    return render(request, 'products/product_confirm_delete.html', {
        'product': product
    })


def catalog(request):
    query = request.GET.get('q', '')
    anime_id = request.GET.get('anime', '')

    products = Product.objects.filter(
        is_active=True,
        stock__gt=0
    )

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

    anime_list = Anime.objects.all().order_by('title')
    products = products.order_by('-created_at')

    return render(request, 'products/catalog.html', {
        'products': products,
        'query': query,
        'anime_id': anime_id,
        'anime_list': anime_list
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = ProductReview.objects.filter(product=product).order_by('-created_at')

    review_form = ProductReviewForm()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form
    })


@login_required
def add_product_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)

        if form.is_valid():
            ProductReview.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment']
                }
            )

            messages.success(request, 'Ulasan produk berhasil dikirim.')
            return redirect('product_detail', product_id=product.id)

    return redirect('product_detail', product_id=product.id)


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'cart/cart.html', {
        'cart': cart
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Cek jika stok awal produk kosong
    if product.stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'pesan': 'Stok produk habis.'})
        messages.error(request, 'Stok produk habis.')
        return redirect('product_detail', product_id=product.id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # Jika barang sudah ada di keranjang, naikkan jumlahnya
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
    else:
        # Jika item baru pertama kali dibuat di DB, quantity otomatis 1 (bawaan default=1)
        pass

    # --- KUNCI NYATA AJAX DI SINI ---
    # Jika request dari JavaScript, langsung potong di sini dan kirim JSON (Jangan biarkan kena fungsi messages Django)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'pesan': f'{product.name} berhasil ditambahkan ke keranjang!'
        })

    # Ini hanya berjalan kalau diakses biasa tanpa AJAX (Fallback)
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

def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')

        if selected_items:
            cart.items.filter(id__in=selected_items).delete()
            messages.success(request, 'Checkout berhasil! Terima kasih atas pembelian Anda.')
        else:
            messages.error(request, 'Tidak ada barang yang dipilih.')

        return redirect('catalog')

    return render(request, 'cart/checkout.html', {
        'cart': cart
    })

# Profile view
@login_required
def buyer_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    is_seller = SellerProfile.objects.filter(user=request.user).exists()

    return render(request, 'profile/buyer_profile.html', {
        'profile': profile,
        'is_seller': is_seller
    })


@login_required
def edit_buyer_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui.')
            return redirect('buyer_profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile/edit_buyer_profile.html', {
        'form': form
    })


def seller_profile(request, seller_id):
    seller = get_object_or_404(
        SellerProfile,
        id=seller_id,
        is_active=True
    )

    products = Product.objects.filter(
        seller=seller,
        is_active=True
    ).order_by('-created_at')

    return render(request, 'profile/seller_profile.html', {
        'seller': seller,
        'products': products
    })


@login_required
def my_seller_profile(request):
    seller = get_object_or_404(SellerProfile, user=request.user)

    products = Product.objects.filter(
        seller=seller
    ).order_by('-created_at')

    return render(request, 'profile/my_seller_profile.html', {
        'seller': seller,
        'products': products
    })


@login_required
def edit_seller_profile(request):
    seller = get_object_or_404(SellerProfile, user=request.user)

    if request.method == 'POST':
        form = SellerProfileEditForm(
            request.POST,
            request.FILES,
            instance=seller
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Profil seller berhasil diperbarui.')
            return redirect('my_seller_profile')
    else:
        form = SellerProfileEditForm(instance=seller)

    return render(request, 'profile/edit_seller_profile.html', {
        'form': form
    })

@staff_member_required(login_url='login')
def review_dashboard(request):
    reviews = Review.objects.all().order_by('-created_at')

    return render(request, 'admin/review_dashboard.html', {
        'reviews': reviews
    })

@login_required
def anime_search_api(request):
    query = request.GET.get('q', '')
    anime_results = []

    if query:
        response = requests.get(
            'https://api.jikan.moe/v4/anime',
            params={
                'q': query,
                'limit': 12
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            anime_results = data.get('data', [])

    return render(request, 'anime/anime_search.html', {
        'query': query,
        'anime_results': anime_results
    })


@login_required
def anime_save(request):
    if request.method == 'POST':
        mal_id = request.POST.get('mal_id')
        title = request.POST.get('title')
        image_url = request.POST.get('image_url')
        synopsis = request.POST.get('synopsis')

        Anime.objects.update_or_create(
            mal_id=mal_id,
            defaults={
                'title': title,
                'image_url': image_url,
                'synopsis': synopsis
            }
        )

        messages.success(request, 'Anime berhasil disimpan ke database.')
        return redirect('anime_search_api')

    return redirect('anime_search_api')

@csrf_exempt
def widget_chat(request):

    print("===== REQUEST MASUK =====")

    if request.method == "POST":

        data = json.loads(request.body)

        question = data.get("message", "")

        print("QUESTION:", question)

        products = search_products(question)

        print("PRODUCT COUNT:", len(products))

        context = build_product_context(products)

        print("CONTEXT:")
        print(context)

        answer = ask_ai(
            question,
            context
        )

        print("ANSWER:")
        print(answer)

        return JsonResponse({
        "answer": answer,
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "price": int(p.price),
                "image": p.image.url if p.image else None,
                "anime": p.anime.title if p.anime else "-",
                "category": p.category.name if p.category else "-"
            }
            for p in products
        ]
    })

    return JsonResponse({
        "error": "Invalid request"
    })


def find_category(question):

    question = question.lower()

    for category in Category.objects.all():

        if category.name.lower() in question:
            return category

    return None

def search_products(question):

    anime = find_anime(question)

    category = find_category(question)

    products = Product.objects.filter(
        is_active=True,
        stock__gt=0
    )

    if anime:
        products = products.filter(
            anime=anime
        )

    if category:
        products = products.filter(
            category=category
        )

    return products[:10]

def get_relevant_products(question):

    keywords = re.findall(r'\w+', question.lower())

    query = Q()

    for keyword in keywords:
        query |= Q(name__icontains=keyword)
        query |= Q(description__icontains=keyword)
        query |= Q(anime__title__icontains=keyword)
        query |= Q(category__name__icontains=keyword)

    return Product.objects.filter(
        query,
        is_active=True
    ).distinct()[:10]

def build_product_context(products):

    context = ""

    for p in products:

        category_name = (
            p.category.name
            if p.category
            else "-"
        )

        anime_name = (
            p.anime.title
            if p.anime
            else "-"
        )

        context += f"""
Nama: {p.name}
Kategori: {category_name}
Anime: {anime_name}
Harga: Rp{int(p.price)}
Stok: {p.stock}
Deskripsi: {p.description}

"""
    return context

def find_anime(question):

    question = question.lower()

    for anime in Anime.objects.all():

        if anime.title.lower() in question:
            return anime

    return None

def chatbot_page(request):
    return render(
        request,
        'chatbox_ai/widget_chat.html'
    )
