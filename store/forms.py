from django import forms
from .models import Review, SellerProfile, Product, ProductReview, UserProfile, ReviewReply


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'rating', 'message']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama kamu'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email kamu'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rating 1 - 5',
                'min': 1,
                'max': 5
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tulis review kamu...',
                'rows': 5
            }),
        }

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['shop_name', 'phone', 'address']

        widgets = {
            'shop_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama toko kamu'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor HP'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Alamat toko',
                'rows': 4
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'anime', 'name', 'description', 'price', 'stock', 'image', 'is_active']

        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'anime': forms.Select(attrs={
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama produk'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Deskripsi produk',
                'rows': 5
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Harga produk'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Stok produk'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']

        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'placeholder': 'Rating 1 - 5'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tulis ulasan produk...',
                'rows': 4
            }),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo', 'bio']

        widgets = {
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ceritakan sedikit tentang kamu...',
                'rows': 4
            }),
        }


class SellerProfileEditForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['shop_name', 'phone', 'address', 'photo', 'bio']

        widgets = {
            'shop_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama toko'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor HP'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Alamat toko',
                'rows': 3
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Deskripsi toko kamu...',
                'rows': 4
            }),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ["message"]

        widgets = {
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Tulis balasan..."
            })
        }