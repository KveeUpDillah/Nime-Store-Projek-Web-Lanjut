import uuid

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_profile'
    )
    photo = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Profile - {self.user.username}"

class SellerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )
    shop_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    photo = models.ImageField(
        upload_to='seller_profiles/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name

class Anime(models.Model):
    mal_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    image_url = models.URLField(blank=True, null=True)
    synopsis = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Product(models.Model):
    seller = models.ForeignKey(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name='products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    anime = models.ForeignKey(
        Anime,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

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

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def formatted_total_price(self):
        return "{:,.0f}".format(self.total_price).replace(",", ".")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity
    
    @property
    def formatted_subtotal(self):
        return "{:,.0f}".format(self.subtotal).replace(",", ".")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Review(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    rating = models.IntegerField(default=5)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.rating}⭐"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
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

class Payment(models.Model):
    """
    Menyimpan data pembayaran QRIS untuk setiap transaksi checkout.
    """

    class PaymentStatus(models.TextChoices):
        PENDING   = 'pending',   'Menunggu Pembayaran'
        PAID      = 'paid',      'Sudah Dibayar'
        EXPIRED   = 'expired',   'Kedaluwarsa'
        CANCELLED = 'cancelled', 'Dibatalkan'

    # Referensi unik tiap transaksi (bisa dikirim ke payment gateway)
    reference_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="ID unik referensi transaksi"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        help_text="Total nominal yang harus dibayar"
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    # URL / base64 string gambar QR dari payment gateway (Xendit, Midtrans, dll)
    qris_image_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL gambar QRIS dari payment gateway"
    )

    # Kode QRIS raw (opsional, untuk generate QR sendiri di frontend)
    qris_string = models.TextField(
        blank=True,
        null=True,
        help_text="Raw string QRIS (EMVCo format)"
    )

    # Waktu kedaluwarsa QR (biasanya 30 menit dari pembuatan)
    expired_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Batas waktu pembayaran QRIS"
    )

    # Waktu konfirmasi pembayaran diterima (diisi oleh webhook/callback)
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Waktu pembayaran dikonfirmasi"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def formatted_amount(self):
        return "{:,.0f}".format(self.amount).replace(",", ".")

    def __str__(self):
        return f"Payment {self.reference_id} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Pembayaran"
        verbose_name_plural = "Pembayaran"


class Checkout(models.Model):
    """
    Menyimpan data pengiriman dan mengikat Cart → Order → Payment.
    """

    class CheckoutStatus(models.TextChoices):
        WAITING_PAYMENT = 'waiting_payment', 'Menunggu Pembayaran'
        PROCESSING      = 'processing',      'Diproses'
        SHIPPED         = 'shipped',         'Dikirim'
        DELIVERED       = 'delivered',       'Diterima'
        CANCELLED       = 'cancelled',       'Dibatalkan'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='checkouts'
    )

    # Relasi ke Order yang dibuat saat checkout
    order = models.OneToOneField(
        'Order',                        # pakai string karena Order ada di file yang sama / di-import
        on_delete=models.CASCADE,
        related_name='checkout'
    )

    # Relasi ke Payment (QRIS)
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkout'
    )

    # ── Data pengiriman ──────────────────────────────────────────────
    recipient_name  = models.CharField(max_length=150, help_text="Nama penerima")
    phone_number    = models.CharField(max_length=20,  help_text="Nomor HP penerima")
    address         = models.TextField(help_text="Alamat lengkap pengiriman")
    city            = models.CharField(max_length=100)
    province        = models.CharField(max_length=100)
    postal_code     = models.CharField(max_length=10)
    notes           = models.TextField(
        blank=True,
        null=True,
        help_text="Catatan tambahan untuk penjual / kurir"
    )

    # ── Status & waktu ───────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=CheckoutStatus.choices,
        default=CheckoutStatus.WAITING_PAYMENT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Checkout #{self.id} - {self.user.username} [{self.get_status_display()}]"

    class Meta:
        verbose_name = "Checkout"
        verbose_name_plural = "Checkout"
        ordering = ['-created_at']