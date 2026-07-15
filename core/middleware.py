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
