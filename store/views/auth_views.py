from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from store.decorators import moderator_required, customer_required
from store.permission import is_moderator
from store.models import SellerProfile
from store.forms import SellerProfileForm


def is_seller(user):
    return hasattr(user, 'seller_profile')


# @moderator_required
# @login_required
# @user_passes_test(is_moderator)
# def dashboard(request):
#     return render(request, 'admin/dashboard.html')


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
            seller_group, created = Group.objects.get_or_create(name='Seller')
            request.user.groups.add(seller_group)
            messages.success(request, 'Akun seller berhasil dibuat.')
            return redirect('seller_dashboard')
    else:
        form = SellerProfileForm()

    return render(request, 'seller/become_seller.html', {'form': form})