from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.models import UserProfile, SellerProfile
from store.forms import UserProfileForm


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
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui.')
            return redirect('buyer_profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile/edit_buyer_profile.html', {'form': form})