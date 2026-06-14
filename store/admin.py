from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at', 'is_visible')
    list_filter = ('rating', 'is_visible', 'created_at')
    search_fields = ('name', 'email', 'message')