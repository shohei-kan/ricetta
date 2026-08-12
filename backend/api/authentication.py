from rest_framework.authentication import SessionAuthentication as DRFSessionAuthentication


class SessionAuthentication(DRFSessionAuthentication):
    """Session authentication that preserves the API's existing 401 response shape."""

    def authenticate_header(self, request):
        return "Session"
