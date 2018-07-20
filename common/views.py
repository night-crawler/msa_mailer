from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from dbmail.views import send_by_dbmail

from common.models import BlacklistRecipient


def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse('')


@csrf_exempt
def send_by_dbmail_custom(request: HttpRequest) -> HttpResponse:
    # simulate success behaviour
    if BlacklistRecipient.match(request.POST.get('recipient', '')):
        return HttpResponse('OK')

    return send_by_dbmail(request)
