from django.db import models
from django.conf import settings
from .catalog_models import Product
from .payment_models import Payment

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        return self.product.price * self.quantity
    
    @property
    def formatted_subtotal(self):
        return "{:,.0f}".format(self.subtotal).replace(",", ".")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"    


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def formatted_total_price(self):
        return "{:,.0f}".format(self.total_price).replace(",", ".")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity
    
    @property
    def formatted_subtotal(self):
        return "{:,.0f}".format(self.subtotal).replace(",", ".")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Checkout(models.Model):
    class CheckoutStatus(models.TextChoices):
        WAITING_PAYMENT = 'waiting_payment', 'Menunggu Pembayaran'
        PROCESSING      = 'processing',      'Diproses'
        SHIPPED         = 'shipped',         'Dikirim'
        DELIVERED       = 'delivered',       'Diterima'
        CANCELLED       = 'cancelled',       'Dibatalkan'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkouts')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='checkout')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='checkout')
    
    recipient_name  = models.CharField(max_length=150, help_text="Nama penerima")
    phone_number    = models.CharField(max_length=20,  help_text="Nomor HP penerima")
    address         = models.TextField(help_text="Alamat lengkap pengiriman")
    city            = models.CharField(max_length=100)
    province        = models.CharField(max_length=100)
    postal_code     = models.CharField(max_length=10)
    notes           = models.TextField(blank=True, null=True, help_text="Catatan tambahan untuk penjual / kurir")
    status = models.CharField(max_length=20, choices=CheckoutStatus.choices, default=CheckoutStatus.WAITING_PAYMENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Checkout #{self.id} - {self.user.username} [{self.get_status_display()}]"

    class Meta:
        verbose_name = "Checkout"
        verbose_name_plural = "Checkout"
        ordering = ['-created_at']