# skt_center/middleware.py

class RemoveCOOPHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.pop("Cross-Origin-Opener-Policy", None)
        response.headers.pop("Cross-Origin-Embedder-Policy", None)
        return response
