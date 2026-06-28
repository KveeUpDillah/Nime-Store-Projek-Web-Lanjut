import os
import re
from django.shortcuts import render
from groq import Groq
from dotenv import load_dotenv
from .models import Anime, Category, Product
from django.db.models import Q

load_dotenv()

client = Groq(
    api_key=("#")
)

SYSTEM_PROMPT = """
Kamu adalah Tom Pearl, AI Assistant resmi Nime Store.

═══════════════════════════════════════
ATURAN ABSOLUT — TIDAK BOLEH DILANGGAR
═══════════════════════════════════════
1. Kamu HANYA boleh menyebut produk yang ADA dalam [KONTEKS PRODUK] yang diberikan.
2. DILARANG KERAS mengarang nama produk, harga, atau detail yang tidak ada di konteks.
3. Jika produk tidak ada di konteks = katakan tidak ada. TITIK.
4. Jika konteks kosong = katakan "Tidak ditemukan produk yang sesuai di database kami."
5. Jangan pernah menggunakan pengetahuanmu sendiri untuk menyebut produk anime manapun.

═══════════════════════
TOPIK YANG BOLEH DIJAWAB
═══════════════════════
- Produk dari [KONTEKS PRODUK] yang diberikan
- Pembelian, penjualan, seller, customer
- Fitur dan cara penggunaan Nime Store

Pertanyaan di luar topik ini → jawab:
"Maaf, saya hanya dapat membantu pertanyaan terkait Nime Store."

═══════════════════════
DILARANG KERAS MEMBERI
═══════════════════════
Source code, struktur database, API key, password, token, data admin, data pengguna lain.

═════════════════════════════
FORMAT REKOMENDASI PRODUK
═════════════════════════════
Jika merekomendasikan produk, WAJIB gunakan format ini persis:

Rekomendasi Produk

1. [Nama Produk dari konteks]
   • Kategori: [dari konteks]
   • Anime: [dari konteks]
   • Harga: Rp[dari konteks]
   • Alasan: [kenapa cocok]

Maksimal 5 produk. Hanya dari konteks. Tidak boleh menambah produk sendiri.
"""

BLOCKED_KEYWORDS = [
    "database",
    "sql",
    "schema",
    "source code",
    "api key",
    "token",
    "password",
    ".env",
    "administrator",
    "admin panel",
    "server",
    "backend",
    "secret"
]

print("=== Nime Store AI Assistant ===")
print("Ketik 'exit' atau 'quit' untuk keluar.\n")

def ask_ai(user_question, product_context):

    print("\n===== USER QUESTION =====")
    print(user_question)

    print("\n===== PRODUCT CONTEXT =====")
    print(product_context)

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "system",
                    "content": product_context
                },
                {
                    "role": "user",
                    "content": user_question
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        print("\n===== RAW RESPONSE =====")
        print(response)

        content = response.choices[0].message.content

        print("\n===== AI CONTENT =====")
        print(content)

        return content

    except Exception as e:

        print("\n===== GROQ ERROR =====")
        print(e)

        return "Terjadi kesalahan AI."

def need_product_recommendation(question):

    keywords = re.findall(r'\w+', question.lower())

    general_keywords = {
    "produk", "barang", "rekomendasi", "cari", "harga",
    "stok", "jual", "beli", "figure", "nendoroid", "merchandise",
    
    "budget", "murah", "terjangkau", "saran", "pilih", "rekomen",
    "dibawah", "under", "maksimal", "ribu", "juta", "ratus",
    
    "satu", "dua", "tiga", "empat", "lima",
    "enam", "tujuh", "delapan", "sembilan", "sepuluh",
    "setengah", "sejuta", "seribu", "seratus"
}

    # cek keyword umum
    if any(word in general_keywords for word in keywords):
        return True

    # cek database
    for word in keywords:

        if Anime.objects.filter(title__icontains=word).exists():
            return True

        if Category.objects.filter(name__icontains=word).exists():
            return True

        if Product.objects.filter(
            Q(name__icontains=word) |
            Q(description__icontains=word)
        ).exists():
            return True

    return False