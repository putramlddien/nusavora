from django import forms
from .models import Restaurant

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            'name', 'description', 'logo', 'address',
            'latitude', 'longitude', 'open_time', 'close_time', 'is_open'
        ]
        widgets = {
            'open_time': forms.TimeInput(attrs={'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'type': 'time'}),
        }
