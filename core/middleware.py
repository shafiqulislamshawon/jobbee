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
    Middleware to ensure REMOTE_ADDR is present in request.META
    to prevent KeyError in packages like django-ratelimit.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'REMOTE_ADDR' not in request.META:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                request.META['REMOTE_ADDR'] = x_forwarded_for.split(',')[0].strip()
            else:
                request.META['REMOTE_ADDR'] = '127.0.0.1'
        return self.get_response(request)
