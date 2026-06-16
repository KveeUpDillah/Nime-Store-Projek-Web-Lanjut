from django.http import HttpResponseForbidden
from django.shortcuts import redirect

# def moderator_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated and request.user.groups.filter(name='Moderator').exists():
#             return view_func(request, *args, **kwargs)
#         else:
#             return HttpResponseForbidden("Kamu tidak memiliki akses ke halaman ini.")
#     return wrapper

def moderator_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Moderator').exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('https://youtu.be/0RdiI1lBttQ?si=E-DzIvnn0lyCef7b')            
    return wrapper

def seller_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Seller').exists():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Kamu tidak memiliki akses ke halaman ini.")
    return wrapper

def customer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Customer').exists():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Kamu tidak memiliki akses ke halaman ini.")
    return wrapper