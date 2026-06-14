from django.shortcuts import render, redirect
from store.models import Product
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Review
from .forms import ReviewForm
from django.contrib import messages

def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

def home(request):
    reviews = Review.objects.filter(is_visible=True).order_by('-created_at')[:6]

    return render(request, 'home.html', {
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

    return render(request, 'support.html', {
        'form': form
    })

def catalog(request):
    products = Product.objects.all()
    return render(request, 'catalog.html', {'products': products})

def contact(request):
    return render(request, 'contact.html')

def gallery(request):   
    return render(request, 'gallery.html')

def support(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Review berhasil dikirim. Terima kasih!')
            return redirect('support')
    else:
        form = ReviewForm()

    return render(request, 'support.html', {
        'form': form
    })

def about(request):
    return render(request, 'about.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "register.html", {
                "pesan": "Password dan konfirmasi password tidak sama."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "pesan": "Username sudah digunakan."
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.save()

        return redirect("login")

    return render(request, "register.html")

# Dashboard view, hanya bisa diakses admin
def is_admin(user):
    return user.groups.filter(name='Moderator').exists()

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, 'admin/dashboard.html')