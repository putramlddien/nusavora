from django import forms
from .models import NusavoraUser

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Konfirmasi Password")
    role = forms.ChoiceField(choices=NusavoraUser.ROLE_CHOICES)
    username = forms.CharField(max_length=50)

    class Meta:
        model = NusavoraUser
        fields = ['username', 'full_name', 'email', 'password', 'password_confirm', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("password_confirm")

        if password != confirm:
            raise forms.ValidationError("Password dan konfirmasi tidak cocok.")

        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')