from django.http import HttpResponse
from django.utils import timezone

import datetime


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'can_request_from_datetime' in request.session:
            #request.session.pop('can_request_from_datetime')
            can_request_from_datetime = request.session.get('can_request_from_datetime')
            if can_request_from_datetime and datetime.datetime.fromisoformat(can_request_from_datetime) > datetime.datetime.now(datetime.timezone.utc):
                return HttpResponse('<h1>Error cookie or javascript disable</h1>', status=401)
        tz_sub_utc_minutes = request.COOKIES.get("tz_sub_utc_minutes")
        if tz_sub_utc_minutes:
            try:
                tz_sub_utc_minutes = int(tz_sub_utc_minutes)
                timezone.activate(datetime.timezone(datetime.timedelta(minutes=tz_sub_utc_minutes)))
            except ValueError:
                timezone.activate(datetime.timezone.utc)
                request.session['can_request_from_datetime'] = (datetime.datetime.now() + datetime.timedelta(minutes=1)).isoformat()
                return HttpResponse('\n<script>'
                                    '\n\tdocument.cookie=`tz_sub_utc_minutes=${-(new Date()).getTimezoneOffset()}`;'
                                    '\n\tlocation.reload();'
                                    '\n</script>')
        else:
            timezone.activate(datetime.timezone.utc)
            request.session['can_request_from_datetime'] = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)).isoformat()
            return HttpResponse('\n<script>'
                                '\n\tdocument.cookie=`tz_sub_utc_minutes=${-(new Date()).getTimezoneOffset()}`;'
                                '\n\tlocation.reload();'
                                '\n</script>')
        response = self.get_response(request)
        response.content = ("\n<script>"
                             "\n\tfunction getCookie(name) {"
                             "\n\t\tconst parts=`; ${document.cookie}`.split(`; ${name}=`);"
                             "\n\t\tif (parts.length >= 2) {"
                             "\n\t\t\tconst value = parts.pop().split(';').shift();"
                             "\n\t\t\treturn value;"
                             "\n\t\t}"
                             "\n\t}"
                             "\n\tif(getCookie('tz_sub_utc_minutes') != -(new Date()).getTimezoneOffset()) {"
                             "\n\t\tdocument.cookie=`tz_sub_utc_minutes=${-(new Date()).getTimezoneOffset()}`; "
                             "\n\t\tlocation.reload();"
                             "\n\t}"
                             "\n</script>").encode() + response.content
        return response
