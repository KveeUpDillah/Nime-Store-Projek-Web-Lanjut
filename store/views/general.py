from django.shortcuts import render, redirect
from django.contrib import messages
from store.models import Product
from store.forms import ReviewForm
from store.models import Review


def index(request):
    products = Product.objects.all()
    return render(request, 'layouts/index.html', {'products': products})


def home(request):
    reviews = Review.objects.filter(is_visible=True).order_by('-created_at')[:6]
    return render(request, 'pages/home.html', {'reviews': reviews})


def support(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_visible = True
            review.save()
            messages.success(request, 'Review berhasil dikirim. Terima kasih!')
            return redirect('support')
    else:
        form = ReviewForm()

    return render(request, 'pages/support.html', {'form': form})


def contact(request):
    return render(request, 'pages/contact.html')


def gallery(request):
    return render(request, 'pages/gallery.html')


def about(request):
    return render(request, 'pages/about.html')


def login(request):
    return render(request, 'accounts/login.html')