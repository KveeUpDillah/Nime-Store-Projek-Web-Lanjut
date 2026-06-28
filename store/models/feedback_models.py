from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .catalog_models import Product

class Review(models.Model):
    """Review Umum / Buku Tamu"""
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    rating = models.IntegerField(default=5)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.rating}⭐"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class ProductReviewImage(models.Model):
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review_images/')

    def __str__(self):
        return f"Review {self.review.id}"
    

class ReviewReply(models.Model):
    review = models.OneToOneField(ProductReview, on_delete=models.CASCADE, related_name="reply")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review reply"
        verbose_name_plural = "Review reply"

    def __str__(self):
        return f"Reply oleh {self.seller.username}"