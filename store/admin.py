from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review, SellerProfile, ProductReview, Cart, CartItem, Anime, Payment, Checkout

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem) 

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at', 'is_visible')
    list_filter = ('rating', 'is_visible', 'created_at')
    search_fields = ('name', 'email', 'message')

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'phone', 'is_active', 'created_at')
    search_fields = ('shop_name', 'user__username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'seller__shop_name')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')   

@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    list_display = ('title', 'mal_id')
    search_fields = ('title',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'amount', 'status', 'paid_at', 'expired_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('reference_id',)
    readonly_fields = ('reference_id', 'created_at', 'updated_at')

@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'recipient_name', 'city', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'recipient_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')