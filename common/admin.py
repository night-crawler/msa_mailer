from django.contrib import admin

from common.models import BlacklistRecipient


@admin.register(BlacklistRecipient)
class BlacklistRecipientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'rx',
    )
    search_fields = ('rx',)
