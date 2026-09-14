import time

from django.http import HttpRequest, HttpResponse


def set_useragent_on_request_middleware(get_response):
    print("initial call")

    def middleware(request: HttpRequest):
        print("before get response")
        request.user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")
        response = get_response(request)
        print("after get response")
        return response

    return middleware

class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print(f"request count: {self.requests_count}")
        response = self.get_response(request)
        self.responses_count += 1
        print(f"response count: {self.responses_count}")
        return response

class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_ip = dict()

    def __call__(self, request: HttpRequest):
        ip = request.META.get("REMOTE_ADDR")
        now = time.time()
        window_start = now - 60

        if ip in self.requests_ip:
            self.requests_ip[ip] = [t for t in self.requests_ip[ip] if t > window_start]
        else:
            self.requests_ip[ip] = []

        if len(self.requests_ip[ip]) >= 30:
            return HttpResponse("Too Many Requests", status = 429)

        self.requests_ip[ip].append(now)
        return self.get_response(request)
