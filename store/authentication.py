from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password   
from django.contrib import messages

from .otp import generate_otp, send_otp_email
from .models import EmailOTP, PendingUser 
from django.utils import timezone
from datetime import timedelta

def login(request):
    template_name = 'accounts/login.html'
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

        otp = generate_otp()

        send_otp_email(email, otp)

        EmailOTP.objects.update_or_create(

            email=email,

            defaults={

                "otp": otp,

                "expired_at": timezone.now() + timedelta(minutes=5),

                "verified": False,

            }

        )

        PendingUser.objects.update_or_create(
                email=email,
                defaults={
                    "username": username,
                    "password": password1,
                }
            )
        request.session["pending_email"] = email

        return redirect("verify_otp")

    return render(request, "accounts/register.html")

def verify_otp(request):
    email = request.session.get("pending_email")
    otp_data = EmailOTP.objects.get(email=email)

    context = {
        "expired_timestamp": int(otp_data.expired_at.timestamp() * 1000)
    }

    if not email:
        return redirect("register")

    if request.method == "POST":

        otp_input = request.POST.get("otp")

        pending_user = PendingUser.objects.get(email=email)

        try:
            otp_data = EmailOTP.objects.get(email=email)

        except EmailOTP.DoesNotExist:

            context["pesan"] = "OTP tidak ditemukan."

            return render(request,
                          "accounts/verify_otp.html",
                          context)
        
        if otp_input != otp_data.otp:
            context["pesan"] = "Kode OTP salah."

            return render(
                request,
                "accounts/verify_otp.html",
                context
            )
        
        if otp_data.is_expired():
            context["pesan"] = "Kode OTP sudah kadaluarsa."

            return render(
                request,
                "accounts/verify_otp.html",
                context
            )
        
        pending_user = PendingUser.objects.get(email=email)
        
        user = User.objects.create_user(
            username=pending_user.username,
            email=pending_user.email,
            password=pending_user.password  
        )

        customer_group, created = Group.objects.get_or_create(
            name="Customer"
        )

        user.groups.add(customer_group)
        user.save()

        auth_login(request, user)
        otp_data.delete()
        pending_user.delete()
        request.session.pop("pending_email", None)
        return redirect("login")
   
    return render(
        request,
        "accounts/verify_otp.html",
        context
    )

def resend_otp(request):

    email = request.session.get("pending_email")

    if not email:
        return redirect("register")

    try:
        otp_data = EmailOTP.objects.get(email=email)

    except EmailOTP.DoesNotExist:
        messages.error(request, "Data OTP tidak ditemukan.")
        return redirect("register")

    # Maksimal kirim ulang 5 kali
    if otp_data.resend_count >= 5:
        messages.error(request, "Batas kirim ulang OTP telah tercapai.")
        return redirect("verify_otp")

    # Tunggu minimal 60 detik
    remaining = timezone.now() - otp_data.last_resend

    if remaining.total_seconds() < 60:

        messages.error(
            request,
            f"Tunggu {60-int(remaining.total_seconds())} detik lagi."
        )

        return redirect("verify_otp")

    # Generate OTP baru
    new_otp = generate_otp()

    otp_data.otp = new_otp
    otp_data.expired_at = timezone.now() + timedelta(minutes=5)
    otp_data.resend_count += 1
    otp_data.last_resend = timezone.now()

    otp_data.save()

    send_otp_email(email, new_otp)

    messages.success(request, "OTP baru berhasil dikirim.")

    return redirect("verify_otp")