import re
import json
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from store.models import Product, Anime, Category
from store.chatbox import ask_ai, SYSTEM_PROMPT, BLOCKED_KEYWORDS


# ── Helpers ──────────────────────────────────────────────────────────────────

def find_category(question):
    question = question.lower()
    for category in Category.objects.all():
        if category.name.lower() in question:
            return category
    return None


def find_anime(question):
    question = question.lower()
    for anime in Anime.objects.all():
        if anime.title.lower() in question:
            return anime
    return None


def extract_price(question):
    question = question.lower()

    # Mapping kata ke angka
    kata_angka = {
        "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5,
        "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9, "sepuluh": 10,
        "setengah": 0.5, "setengah juta": 500_000
    }

    # Format: "di bawah satu juta", "under dua juta", "dibawah lima ratus ribu"
    for kata, nilai in kata_angka.items():
        # Juta
        if re.search(rf'(di\s*bawah|under|maksimal|max|kurang dari)\s*{kata}\s*juta', question):
            return int(nilai * 1_000_000)
        # Ribu
        if re.search(rf'(di\s*bawah|under|maksimal|max|kurang dari)\s*{kata}\s*ribu', question):
            return int(nilai * 1_000)

    # Format angka biasa: "di bawah 500000", "di bawah 1jt", "dibawah 500rb"
    match = re.search(r'(di\s*bawah|under|maksimal|max|kurang dari)\s*(\d+)\s*juta', question)
    if match:
        return int(match.group(2)) * 1_000_000

    match = re.search(r'(di\s*bawah|under|maksimal|max|kurang dari)\s*(\d+)\s*(ribu|rb)', question)
    if match:
        return int(match.group(2)) * 1_000

    # Shorthand: "1jt", "500rb"
    match = re.search(r'(\d+)\s*jt', question)
    if match:
        return int(match.group(1)) * 1_000_000

    match = re.search(r'(\d+)\s*rb', question)
    if match:
        return int(match.group(1)) * 1_000

    # Format: "budget 500000"
    match = re.search(r'budget\s*(\d+)', question)
    if match:
        return int(match.group(1))

    return None


def search_products(question, max_price=None):
    keywords = re.findall(r'\w+', question.lower())

    STOPWORDS = {
        "apa", "yang", "dan", "di", "ke", "dari",
        "cara", "bagaimana", "tolong", "saya",
        "ingin", "ada", "kah", "untuk, hei"
    }

    keywords = [k for k in keywords if k not in STOPWORDS and len(k) > 2]

    aliases = {
        "merch": "merchandise",
        "fig": "figure",
        "nendo": "nendoroid",
    }

    if not keywords:
        return Product.objects.none()

    query = Q()
    for keyword in keywords:
        query |= Q(name__icontains=keyword)
        query |= Q(description__icontains=keyword)
        query |= Q(anime__title__icontains=keyword)
        query |= Q(category__name__icontains=keyword)
        query |= Q(name__icontains="merchandise")

    qs = Product.objects.filter(query, is_active=True, stock__gt=0).distinct()

    if max_price:
        qs = qs.filter(price__lte=max_price)

    return qs[:8]


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


def build_product_context(products, max_price=None):
    
    if not products or not products.exists():
        return """[KONTEKS PRODUK]
        KOSONG. Tidak ada produk yang ditemukan.
        INSTRUKSI KERAS: DILARANG MUTLAK mengarang, menyebut, atau merekomendasikan produk apapun.
        Jawab hanya: "Maaf, tidak ada produk yang sesuai dengan kriteria tersebut di Nime Store."
        JANGAN tambahkan kalimat lain apapun."""

    header = "[KONTEKS PRODUK]\n"
    header += "Berikut adalah SATU-SATUNYA daftar produk yang boleh kamu rekomendasikan.\n"
    header += "DILARANG menyebut produk di luar daftar ini.\n"
    
    if max_price:
        header += f"Filter harga aktif: maksimal Rp{max_price:,}\n"
    
    header += f"Total produk tersedia: {products.count()}\n"
    header += "=" * 40 + "\n"

    context = header
    for i, p in enumerate(products, start=1):
        category_name = p.category.name if p.category else "-"
        anime_name = p.anime.title if p.anime else "-"
        context += f"""
[Produk {i}]
Nama: {p.name}
Kategori: {category_name}
Anime: {anime_name}
Harga: Rp{int(p.price):,}
Stok: {p.stock}
Deskripsi: {p.description}
"""

    context += "\n" + "=" * 40
    context += "\nINGAT: Hanya rekomendasikan produk dari daftar [Produk 1] s/d [Produk " + str(products.count()) + "] di atas."

    return context


# ── Views ─────────────────────────────────────────────────────────────────────

@csrf_exempt
def widget_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        question = data.get("message", "").lower()

        for keyword in BLOCKED_KEYWORDS:
            if keyword in question:
                return JsonResponse({
                    "answer": "Maaf, saya tidak dapat membantu dengan permintaan tersebut.",
                    "products": []
                })

        max_price = extract_price(question)
        products = search_products(question, max_price=max_price)
        context = build_product_context(products, max_price=max_price)

        # ✅ Tambah ini sementara
        print("QUESTION:", question)
        print("MAX PRICE:", max_price)
        print("PRODUCTS COUNT:", products.count())
        print("CONTEXT:", context)

        answer = ask_ai(question, context)

        print("ANSWER:", answer)

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

    return JsonResponse({"error": "Invalid request"})


def chatbot_page(request):
    return render(request, 'chatbox_ai/widget_chat.html')


# ── Anime CRUD ────────────────────────────────────────────────────────────────

@login_required
def anime_search_api(request):
    query = request.GET.get('q', '')
    anime_results = []

    if query:
        response = requests.get(
            'https://api.jikan.moe/v4/anime',
            params={'q': query, 'limit': 12},
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