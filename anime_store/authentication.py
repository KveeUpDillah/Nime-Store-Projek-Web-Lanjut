from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render

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