from django.urls import path
from store.views import admin_views as v

urlpatterns = [
    # Dashboard
    path('admin-panel/',                          v.admin_dashboard,                  name='admin_dashboard'),

    # Produk
    path('admin-panel/products/',                 v.admin_products,                   name='admin_products'),
    path('admin-panel/products/<int:pk>/delete/', v.admin_product_delete,             name='admin_product_delete'),

    # Kategori
    path('admin-panel/categories/',               v.admin_categories,                 name='admin_categories'),
    path('admin-panel/categories/create/',        v.admin_category_create,            name='admin_category_create'),
    path('admin-panel/categories/<int:pk>/edit/', v.admin_category_edit,              name='admin_category_edit'),
    path('admin-panel/categories/<int:pk>/delete/', v.admin_category_delete,          name='admin_category_delete'),

    # Anime
    path('admin-panel/anime/',                    v.admin_anime,                      name='admin_anime'),
    path('admin-panel/anime/<int:pk>/delete/',    v.admin_anime_delete,               name='admin_anime_delete'),

    # Order
    path('admin-panel/orders/',                   v.admin_orders,                     name='admin_orders'),
    path('admin-panel/orders/<int:pk>/',          v.admin_order_detail,               name='admin_order_detail'),
    path('admin-panel/orders/<int:pk>/delete/',   v.admin_order_delete,               name='admin_order_delete'),

    # Checkout
    path('admin-panel/checkouts/',                v.admin_checkouts,                  name='admin_checkouts'),
    path('admin-panel/checkouts/<int:pk>/status/', v.admin_checkout_update_status,    name='admin_checkout_update_status'),
    path('admin-panel/checkouts/<int:pk>/delete/', v.admin_checkout_delete,           name='admin_checkout_delete'),

    # Pembayaran
    path('admin-panel/payments/',                 v.admin_payments,                   name='admin_payments'),
    path('admin-panel/payments/<int:pk>/delete/', v.admin_payment_delete,             name='admin_payment_delete'),

    # User
    path('admin-panel/users/',                    v.admin_users,                      name='admin_users'),
    path('admin-panel/users/<int:pk>/delete/',    v.admin_user_delete,                name='admin_user_delete'),

    # Seller
    path('admin-panel/sellers/',                  v.admin_sellers,                    name='admin_sellers'),
    path('admin-panel/sellers/<int:pk>/toggle/',  v.admin_seller_toggle,              name='admin_seller_toggle'),
    path('admin-panel/sellers/<int:pk>/delete/',  v.admin_seller_delete,              name='admin_seller_delete'),

    # Review
    path('admin-panel/reviews/',                  v.admin_reviews,                    name='admin_reviews'),
    path('admin-panel/reviews/<int:pk>/toggle/',  v.admin_review_toggle_visibility,   name='admin_review_toggle'),
    path('admin-panel/reviews/<int:pk>/delete/',  v.admin_review_delete,              name='admin_review_delete'),
    path('admin-panel/product-reviews/<int:pk>/delete/', v.admin_product_review_delete, name='admin_product_review_delete'),
]