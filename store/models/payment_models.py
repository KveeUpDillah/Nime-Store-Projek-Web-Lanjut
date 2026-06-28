import uuid
from django.db import models

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING   = 'pending',   'Menunggu Pembayaran'
        PAID      = 'paid',      'Sudah Dibayar'
        EXPIRED   = 'expired',   'Kedaluwarsa'
        CANCELLED = 'cancelled', 'Dibatalkan'

    reference_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, help_text="ID unik referensi transaksi")
    amount = models.DecimalField(max_digits=12, decimal_places=0, help_text="Total nominal yang harus dibayar")
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    qris_image_url = models.URLField(blank=True, null=True, help_text="URL gambar QRIS dari payment gateway")
    qris_string = models.TextField(blank=True, null=True, help_text="Raw string QRIS (EMVCo format)")
    expired_at = models.DateTimeField(blank=True, null=True, help_text="Batas waktu pembayaran QRIS")
    paid_at = models.DateTimeField(blank=True, null=True, help_text="Waktu pembayaran dikonfirmasi")
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