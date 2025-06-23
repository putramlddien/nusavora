from django import forms
from .models import Product, Category
from django.db.models import Q

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'image', 'price', 'is_available', 'is_customizable']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Ambil merchant/restaurant yang dikirim dari views
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        
        if restaurant:
            self.fields['category'].queryset = Category.objects.filter(
                Q(is_global=True) | Q(merchant=restaurant)
            )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
