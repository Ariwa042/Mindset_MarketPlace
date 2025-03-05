from django.contrib import admin
from .models import PiWallet, PiTransaction

@admin.register(PiWallet)
class PiWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'connected_at']
    list_filter = ['is_verified', 'connected_at']
    search_fields = ['user__email', 'passphrase']
    readonly_fields = ['connected_at', 'last_verified', 'view_passphrase']
    
    def view_passphrase(self, obj):
        return f"""
        <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace;">
            {obj.passphrase}
        </div>
        """
    view_passphrase.short_description = 'Wallet Passphrase'
    view_passphrase.allow_tags = True

@admin.register(PiTransaction)
class PiTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['wallet__user__email', 'transaction_hash']
    readonly_fields = ['created_at', 'updated_at']
