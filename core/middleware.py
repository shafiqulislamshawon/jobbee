import pytz
from django.utils import timezone

class TimezoneMiddleware:
    """
    Middleware to activate the user's timezone if it exists in their session.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get('django_timezone')
        if tzname:
            try:
                timezone.activate(pytz.timezone(tzname))
            except pytz.UnknownTimeZoneError:
                timezone.deactivate()
        else:
            timezone.deactivate()
            
        return self.get_response(request)


class RemoteAddrMiddleware:
    """
    Ensure REMOTE_ADDR is available for Django packages
    that expect it.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.META.get('REMOTE_ADDR'):
            x_real_ip = request.META.get('HTTP_X_REAL_IP')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

            if x_real_ip:
                request.META['REMOTE_ADDR'] = x_real_ip
            elif x_forwarded_for:
                request.META['REMOTE_ADDR'] = (
                    x_forwarded_for.split(',')[0].strip()
                )
            else:
                request.META['REMOTE_ADDR'] = '127.0.0.1'

        return self.get_response(request)
