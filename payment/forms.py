from django import forms
from mnemonic import Mnemonic
from .models import PiWallet

class PassphraseForm(forms.Form):
    passphrase = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Enter your 24-word Pi passphrase'
        })
    )

    def clean_passphrase(self):
        passphrase = self.cleaned_data['passphrase']
        words = passphrase.strip().split()
        
        if len(words) != 24:
            raise forms.ValidationError("Passphrase must contain exactly 24 words.")
        
        # Validate using mnemonic library
        mnemo = Mnemonic("english")
        if not mnemo.check(" ".join(words)):
            raise forms.ValidationError("Invalid mnemonic passphrase.")
        
        return passphrase
