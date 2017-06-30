import re

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BlacklistRecipient(models.Model):
    rx = models.CharField(_('regular expression'), max_length=255)
    enabled = models.BooleanField(_('enabled'), default=True)

    class Meta:
        verbose_name = _('blacklist item')
        verbose_name_plural = _('blacklist items')

    def __str__(self) -> str:
        return 'Blacklist: %s' % self.rx

    @staticmethod
    def match(recipient: str) -> bool:
        for item in BlacklistRecipient.objects.filter(enabled=True):
            _rx = re.compile(item.rx)
            if _rx.match(recipient):
                return True
        return False
