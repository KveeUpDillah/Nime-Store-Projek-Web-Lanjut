from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, Group

def login(request):
    template_name = 'login.html'
    pesan = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            pesan = "Username dan Password harus diisi yah~"
        else:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                if user.groups.filter(name='Moderator').exists():
                    print("--> Masuk sebagai Moderator, mengalihkan...")
                    return redirect('dashboard')
                else:
                    print("--> Masuk sebagai Viewer, mengalihkan...")
                    return redirect('home')
            else:
                pesan = "Username atau password kamu salah!"
                print("--> Hasil: Autentikasi gagal (User tidak ditemukan/salah password)")

    return render(request, template_name, {'pesan': pesan})


# logic back-end terkait urusan register
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "accounts/register.html", {
                "pesan": "Password dan konfirmasi password tidak sama."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/register.html", {
                "pesan": "Username sudah digunakan."
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        customer_group = Group.objects.get(name='Customer')
        user.groups.add(customer_group)

        user.save()

        return redirect("login")

    return render(request, "accounts/register.html")