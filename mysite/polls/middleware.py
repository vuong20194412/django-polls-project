from django.http import HttpResponse
from django.utils import timezone

import datetime


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_sub_utc_minutes = request.COOKIES.get("tz_sub_utc_minutes")
        if tz_sub_utc_minutes:
            try:
                tz_sub_utc_minutes = int(tz_sub_utc_minutes)
                timezone.activate(datetime.timezone(datetime.timedelta(minutes=tz_sub_utc_minutes)))
            except ValueError:
                timezone.activate(datetime.timezone.utc)
                return HttpResponse(self.get_html_code_of_tz_sub_utc_minutes())
        else:
            timezone.activate(datetime.timezone.utc)
            return HttpResponse(self.get_html_code_of_tz_sub_utc_minutes())
        response = self.get_response(request)
        response.content = self.get_html_code_of_tz_sub_utc_minutes().encode() + response.content
        return response

    def get_html_code_of_tz_sub_utc_minutes(self):
        text = ('\n<noscript><h1>Please enable javascript and try again.</h1></noscript>\n<script>'
                '\n\tfunction getCookie(name) {'
                '\n\t\tconst parts=`; ${document.cookie}`.split(`; ${name}=`);'
                '\n\t\tif (parts.length >= 2) {'
                '\n\t\t\tconst value = parts.pop().split(";").shift();'
                '\n\t\t\treturn value;'
                '\n\t\t}'
                '\n\t}'
                '\n\tif(!getCookie("tz_sub_utc_minutes")) {'
                '\n\t\tconst cookies = document.cookie'
                '\n\t\tdocument.cookie=`tz_sub_utc_minutes=${-(new Date()).getTimezoneOffset()}`;'
                '\n\t\tif(!getCookie("tz_sub_utc_minutes")) {'
                '\n\t\t\tdebugger'
                '\n\t\t\tdocument.write("<h1>Please enable cookies and try again.</h1>")'
                '\n\t\t}'
                '\n\t\telse {'
                '\n\t\t\tdebugger'
                '\n\t\t\tlocation.reload();'
                '\n\t\t}'
                '\n\t}'
                '\n\telse if(getCookie("tz_sub_utc_minutes") != -(new Date()).getTimezoneOffset()) {'
                '\n\t\tconst cookies = document.cookie'
                '\n\t\tdebugger'
                '\n\t\tdocument.cookie=`tz_sub_utc_minutes=${-(new Date()).getTimezoneOffset()}`; '
                '\n\t\tlocation.reload();'
                '\n\t}'
                '\n</script>')
        return text