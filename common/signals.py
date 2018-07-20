import re

from django.db.models.signals import pre_save
from django.dispatch import receiver

from dbmail.models import MailTemplate

broken_rx = re.compile(r'')


@receiver(pre_save, sender=MailTemplate, dispatch_uid='mailtemplate_pre_save')
def mailtemplate_pre_save(sender, instance: MailTemplate, **kwargs):
    instance.message = instance.message.replace('%7B%7B', '{{')
    instance.message = instance.message.replace('%7b%7b', '{{')
    instance.message = instance.message.replace('%7D%7D', '}}')
    instance.message = instance.message.replace('%7d%7d', '}}')
