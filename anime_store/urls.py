from django.urls import path, include
from django.contrib import admin
from store import authentication, views
from store.views import admin_views as v
from store.authentication import login as auth_login_view
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='root'),
    path('', include('store.admin_urls')),
    path('admin/', admin.site.urls),

    # Login/Logout 
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', authentication.register, name='register'),

    path('index/', views.index, name='index'),
    path('home/', views.home, name='home'),

    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('support/', views.support, name='support'),
    path('about/', views.about, name='about'),

    path('become-seller/', views.become_seller, name='become_seller'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/order/<int:checkout_id>/confirm/', views.confirm_payment, name='confirm_payment'),

    path('seller/product/create/', views.product_create, name='product_create'),
    path('seller/product/<int:product_id>/edit/', views.product_update, name='product_update'),
    path('seller/product/<int:product_id>/delete/', views.product_delete, name='product_delete'),

    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.add_product_review, name='add_product_review'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path("orders/cancel/<int:checkout_id>/", views.cancel_order, name="cancel_order"),

    path('orders/cust_orders/', views.cust_orders, name='cust_orders'),
    path('orders/<int:checkout_id>/receipt/', views.receipt_data, name='receipt_data'),
    path('orders/<int:checkout_id>/receipt/pdf/', views.receipt_pdf, name='receipt_pdf'),

    path('profile/', views.buyer_profile, name='buyer_profile'),
    path('profile/edit/', views.edit_buyer_profile, name='edit_buyer_profile'),

    path('seller/profile/', views.my_seller_profile, name='my_seller_profile'),
    path('seller/profile/edit/', views.edit_seller_profile, name='edit_seller_profile'),

    path('seller/<int:seller_id>/', views.seller_profile, name='seller_profile'),

    path('dashboard/reviews/', views.review_dashboard, name='review_dashboard'),
    path("review/<int:review_id>/reply/", views.reply_review,name="reply_review"),

    path('anime/search/', views.anime_search_api, name='anime_search_api'),
    path('anime/save/', views.anime_save, name='anime_save'),

    path('chatbox_ai/widget_chat/', views.widget_chat, name='widget_chat'),
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)