from django import forms
from mnemonic import Mnemonic
from .models import PiWallet

class PassphraseForm(forms.Form):
    passphrase = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your 24-word recovery phrase'
        })
    )

    def clean_passphrase(self):
        passphrase = self.cleaned_data['passphrase'].strip().lower()
        words = passphrase.split()
        
        if len(words) != 24:
            raise forms.ValidationError('Please enter exactly 24 words')
        
        # Additional validation if needed
        for word in words:
            if not word.isalpha():
                raise forms.ValidationError('Recovery phrase should only contain letters')
        
        return ' '.join(words)  # Normalize the passphrase
