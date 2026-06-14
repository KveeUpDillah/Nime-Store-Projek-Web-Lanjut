from django import forms
from .models import Review


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