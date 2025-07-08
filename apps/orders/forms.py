from django import forms
from .models import Order

class CheckoutForm(forms.Form):
    delivery_type = forms.ChoiceField(choices=Order.DELIVERY_TYPE_CHOICES)
    delivery_address = forms.CharField(required=False)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('delivery_type') == 'delivery' and not cleaned.get('delivery_address'):
            self.add_error('delivery_address', 'Alamat wajib diisi untuk delivery.')
        return cleaned
