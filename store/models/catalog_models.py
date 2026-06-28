from django.db import models
from .account_models import SellerProfile  # Import dari file sejenis jika dibutuhkan

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Anime(models.Model):
    mal_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    image_url = models.URLField(blank=True, null=True)
    synopsis = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    anime = models.ForeignKey(Anime, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def formatted_price(self):
        return "{:,.0f}".format(self.price).replace(",", ".")

    @property
    def is_sold_out(self):
        return self.stock <= 0

    def __str__(self):
        return self.name